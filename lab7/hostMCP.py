import os
import json
import requests
import datetime
from fastmcp import Client
import time
import logging
from typing import List, Dict, Any
import asyncio 

# Konfiguracja logowania do konsoli
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- STAŁE KONFIGURACYJNE ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
HOST = "127.0.0.1" 
PORT = 8000
# Adres serwera MCP (FastMCP domyślnie używa /mcp dla SSE/HTTP)
LOCAL_SERVER_ADDRESS_MCP = f"http://{HOST}:{PORT}/mcp" 
LOG_FILE = "log.txt"
MAX_RETRIES = 3
MAX_HISTORY_LENGTH = 20

# Klucz API (pobierany ze zmiennej środowiskowej)
API_KEY = os.getenv("GEMINI_API_KEY")

# --- FUNKCJE POMOCNICZE ---

def log_interaction(type: str, content: str):
    """Loguje interakcję do pliku log.txt i konsoli."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{type}]: {content}\n"
    print(log_entry.strip())
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"BŁĄD logowania do pliku {LOG_FILE}: {e}")

# --- GŁÓWNA KLASA HOSTU MCP ---

class GeminiMcpHost:
    def __init__(self):
        if not API_KEY:
            raise EnvironmentError("Błąd: Zmienna środowiskowa GEMINI_API_KEY nie jest ustawiona.")
            
        self.history: List[Dict[str, Any]] = []
        self.tool_definitions: List[Dict[str, Any]] = []
        self.is_connected = False 
        self.tool_names = set() 
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"--- Początek sesji: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        
        log_interaction("SYSTEM", f"Host MCP uruchomiony. Klient łączy się z: {LOCAL_SERVER_ADDRESS_MCP}")

    async def initialize_client(self):
        """
        Inicjalizuje klienta FastMCP i wykonuje Discovery narzędzi.
        """
        try:
            # Tworzenie tymczasowego klienta z URL
            temp_client = Client(LOCAL_SERVER_ADDRESS_MCP)
            
            # Używamy context managera, który automatycznie nawiązuje połączenie
            async with temp_client:
                # Pobieramy listę narzędzi używając standardowej metody MCP
                # W tej wersji FastMCP, list_tools() zwraca bezpośrednio listę, a nie obiekt z atrybutem .tools
                tools_list = await temp_client.list_tools()
                
                if not tools_list:
                    log_interaction("OSTRZEŻENIE", f"Nie wykryto narzędzi na serwerze {LOCAL_SERVER_ADDRESS_MCP}.")
                else:
                    self.tool_definitions = []
                    self.tool_names = set()
                    
                    # Konwersja narzędzi MCP na format Google Function Calling
                    for tool in tools_list:
                        self.tool_names.add(tool.name)
                        self.tool_definitions.append({
                            "functionDeclarations": [{
                                "name": tool.name,
                                "description": tool.description or "Brak opisu.",
                                # W MCP schema jest w polu inputSchema
                                "parameters": tool.inputSchema or {"type": "object", "properties": {}},
                            }]
                        })
                    
                    # Dodanie Google Search jako opcji (Grounding)
                    self.tool_definitions.append({"google_search": {}})
                    
                    tool_names_list = list(self.tool_names)
                    log_interaction("SUKCES", f"Odkryto narzędzia: {tool_names_list}")
                    self.is_connected = True
            
        except Exception as e:
            log_interaction("BŁĄD", f"Nie udało się połączyć z serwerem MCP lub odkryć narzędzi: {e}")
            self.is_connected = False


    async def run_tool_call(self, function_call: dict) -> dict:
        """Wykonuje wywołanie narzędzia przez klienta FastMCP w kontekście asynchronicznym."""
        name = function_call.get("name")
        args = function_call.get("args", {})
        
        log_interaction("TOOL_CALL", f"Model chce wywołać narzędzie: {name} z parametrami: {args}")
        
        # Nowa instancja klienta dla każdego wywołania (stateless)
        temp_client = Client(LOCAL_SERVER_ADDRESS_MCP)
        
        if self.is_connected and name in self.tool_names: 
            try:
                async with temp_client:
                    # Wywołanie narzędzia z argumentami
                    result = await temp_client.call_tool(name, arguments=args)
                    
                    # FastMCP zwraca obiekt CallToolResult, musimy wydobyć treść
                    # Zazwyczaj wynik jest w result.content (lista obiektów TextContent lub ImageContent)
                    content_text = ""
                    if hasattr(result, 'content') and result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                content_text += content.text
                    else:
                        content_text = str(result)

                    log_interaction("TOOL_RESULT", f"Rezultat narzędzia {name}: {content_text}")
                    
                    # Zwracamy w formacie oczekiwanym przez Gemini
                    return {
                        "functionResponse": {
                            "name": name,
                            "response": {"result": content_text} 
                        }
                    }
            except Exception as e:
                error_msg = f"Błąd wykonania narzędzia {name}: {e}"
                log_interaction("BŁĄD_NARZĘDZIA", error_msg)
                return {
                    "functionResponse": {
                        "name": name,
                        "response": {"error": error_msg}
                    }
                }
        else:
            error_msg = f"Narzędzie {name} jest niedostępne."
            log_interaction("BŁĄD_NARZĘDZIA", error_msg)
            return {
                "functionResponse": {
                    "name": name,
                    "response": {"error": error_msg}
                }
            }


    async def send_to_gemini(self, user_prompt: str):
        """Główna funkcja do komunikacji z Gemini API."""
        
        if len(self.history) > MAX_HISTORY_LENGTH:
             self.history = self.history[-MAX_HISTORY_LENGTH:]
             
        self.history.append({"role": "user", "parts": [{"text": user_prompt}]})
        log_interaction("USER_PROMPT", user_prompt)
        
        payload = {
            "contents": self.history,
            "tools": self.tool_definitions if self.is_connected else [{"google_search": {}}], 
        }
        api_url_with_key = f"{GEMINI_API_URL}?key={API_KEY}"
        
        max_tool_turns = 5
        for turn in range(max_tool_turns):
            for attempt in range(MAX_RETRIES):
                try:
                    response = await asyncio.to_thread(
                        requests.post, api_url_with_key, json=payload
                    )
                    
                    if response.status_code >= 500:
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        else:
                            response.raise_for_status()
                    
                    response.raise_for_status()
                    result = response.json()
                    break
                
                except requests.exceptions.RequestException as e:
                    error_details = response.text if 'response' in locals() else "Brak odpowiedzi"
                    log_interaction("BŁĄD_REQUEST", f"Błąd komunikacji z Gemini API: {e}. Szczegóły: {error_details}")
                    if attempt == MAX_RETRIES - 1:
                        return
            
            candidate = result.get("candidates", [{}])[0]
            content = candidate.get("content", {})
            
            function_calls_parts = [p for p in content.get("parts", []) if "functionCall" in p]
            
            if function_calls_parts:
                tool_calls_results = []
                
                for part in function_calls_parts:
                    function_call = part["functionCall"]
                    # Poprawka: Model Gemini powinien automatycznie obsługiwać 'google_search', 
                    # więc interesują nas tylko narzędzia MCP.
                    if function_call.get('name') in self.tool_names:
                        tool_results = await self.run_tool_call(function_call)
                        tool_calls_results.append(tool_results)
                    # W przeciwnym razie jest to nieznane narzędzie, które nie jest google_search
                    elif function_call.get('name') != 'google_search':
                         error_msg = f"Model próbował wywołać nieznane narzędzie: {function_call.get('name')}"
                         log_interaction("BŁĄD_NARZĘDZIA", error_msg)
                         tool_calls_results.append({
                            "functionResponse": {
                                "name": function_call.get('name'),
                                "response": {"error": error_msg}
                            }
                        })

                self.history.append({"role": "model", "parts": function_calls_parts})
                # Dodajemy tylko te wyniki, które pochodzą z faktycznie obsłużonych narzędzi MCP
                if tool_calls_results:
                    self.history.append({"role": "tool", "parts": tool_calls_results})
                payload["contents"] = self.history
                
                if turn == max_tool_turns - 1:
                    log_interaction("OSTRZEŻENIE", "Przekroczono limit tur.")
                    return 
            
            elif content.get("parts") and "text" in content["parts"][0]:
                model_response_text = content["parts"][0]["text"]
                self.history.append({"role": "model", "parts": [{"text": model_response_text}]})
                log_interaction("GEMINI_RESPONSE", model_response_text)
                return
            
            else:
                log_interaction("BŁĄD_API", "Nieoczekiwana odpowiedź z API.")
                return

    async def async_run(self):
        """Asynchroniczna metoda uruchamiająca sesję."""
        await self.initialize_client()
        
        if not self.is_connected:
             print("\n--- BŁĄD: Brak połączenia z serwerem MCP. ---")
        
        print("\n--- Start Chatu ---")
        print("Wpisz 'koniec' aby zakończyć.")
        
        while True:
            try:
                user_input = await asyncio.to_thread(input, "\nTy: ")
                user_input = user_input.strip()
                
                if user_input.lower() in ["koniec", "exit"]:
                    log_interaction("SYSTEM", "Koniec sesji.")
                    break
                
                if user_input:
                    await self.send_to_gemini(user_input)

            except KeyboardInterrupt:
                log_interaction("SYSTEM", "Przerwano (Ctrl+C).")
                break
            except Exception as e:
                log_interaction("FATAL_ERROR", f"Krytyczny błąd: {e}")
                break

if __name__ == "__main__":
    try:
        host = GeminiMcpHost()
        asyncio.run(host.async_run())
    except EnvironmentError as e:
        print(e)
    except Exception as e:
        print(f"Błąd inicjalizacji: {e}")