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
# Zmiana modelu na stabilny 'gemini-2.5-flash', aby obsługiwał funkcje narzędziowe.
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
HOST = "127.0.0.1" 
PORT = 8000
# Adres serwera MCP (FastMCP domyślnie używa /mcp dla SSE/HTTP)
LOCAL_SERVER_ADDRESS_MCP = f"http://{HOST}:{PORT}/mcp" 
LOG_FILE = "log.txt"
MAX_RETRIES = 3
MAX_HISTORY_LENGTH = 20

# Klucz API (pobierany ze zmiennej środowiskowej)
# PAMIĘTAJ: Musisz ustawić zmienną GEMINI_API_KEY w terminalu
# UWAGA: Twój klucz API WYGASŁ (API key expired), musisz go odnowić/zmienić.
API_KEY = os.getenv("GEMINI_API_KEY")

# Stała konfiguracja dla Google Search, używana tylko, gdy nie ma narzędzi MCP.
GOOGLE_SEARCH_TOOL = [{"google_search": {}}]

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
        # tool_definitions będą zawierać TYLKO funkcje FastMCP
        self.tool_definitions: List[Dict[str, Any]] = []
        self.is_connected = False 
        self.tool_names = set() 
        
        # Resetowanie pliku logu
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"--- Początek sesji: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        
        log_interaction("SYSTEM", f"Host MCP uruchomiony. Klient łączy się z: {LOCAL_SERVER_ADDRESS_MCP}")

    async def initialize_client(self):
        """
        Inicjalizuje klienta FastMCP i wykonuje Discovery narzędzi.
        Dodatkowo naprawia znane niezgodności w nazwach parametrów, zmieniając 
        nazwę 'lata_czlowieka' na 'wiek' w schemacie dla Gemini.
        """
        try:
            temp_client = Client(LOCAL_SERVER_ADDRESS_MCP)
            
            async with temp_client:
                tools_list = await temp_client.list_tools()
                
                if not tools_list:
                    log_interaction("OSTRZEŻENIE", f"Nie wykryto narzędzi na serwerze {LOCAL_SERVER_ADDRESS_MCP}.")
                else:
                    self.tool_definitions = []
                    self.tool_names = set()
                    
                    # Konwersja narzędzi MCP na format Google Function Calling
                    for tool in tools_list:
                        tool_name = tool.name
                        self.tool_names.add(tool_name)
                        
                        tool_schema = tool.inputSchema or {"type": "object", "properties": {}}
                        
                        # --- POPRAWKA SPECYFICZNA DLA NARZĘDZIA 'oblicz_wiek_psa' ---
                        # Zmieniamy nazwy argumentów w schemacie PRZED wysłaniem do Gemini,
                        # aby model używał prostszego terminu 'wiek'.
                        if tool_name == "oblicz_wiek_psa" and tool_schema.get("properties"):
                            if "lata_czlowieka" in tool_schema["properties"]:
                                # Przepisujemy schemat, aby używał nazwy 'wiek', którą model Gemini preferuje.
                                tool_schema["properties"]["wiek"] = tool_schema["properties"].pop("lata_czlowieka")
                                # Aktualizujemy listę wymaganych argumentów
                                if "required" in tool_schema and "lata_czlowieka" in tool_schema["required"]:
                                    tool_schema["required"].remove("lata_czlowieka")
                                    tool_schema["required"].append("wiek")
                                log_interaction("PATCH", "Naprawiono schemat 'oblicz_wiek_psa', zmieniono 'lata_czlowieka' na 'wiek' w definicji dla Gemini.")
                        # -----------------------------------------------------------------

                        # Dodajemy definicję narzędzia
                        self.tool_definitions.append({
                            # Używamy formatu Function Calling
                            "functionDeclarations": [{
                                "name": tool_name,
                                "description": tool.description or "Brak opisu.",
                                "parameters": tool_schema,
                            }]
                        })
                    
                    tool_names_list = list(self.tool_names)
                    log_interaction("SUKCES", f"Odkryto narzędzia: {tool_names_list}. Google Search będzie używane jako fallback.")
                    self.is_connected = True
            
        except Exception as e:
            log_interaction("BŁĄD", f"Nie udało się połączyć z serwerem MCP lub odkryć narzędzi: {e}")
            self.is_connected = False


    async def run_tool_call(self, function_call: dict) -> dict:
        """Wykonuje wywołanie narzędzia przez klienta FastMCP w kontekście asynchronicznym."""
        name = function_call.get("name")
        args = function_call.get("args", {})
        
        # --- KOREKTA DLA NARZĘDZIA 'oblicz_wiek_psa' ---
        # MUSIMY PRZEMAPOWAĆ KLUCZ Z GEMINI ('wiek') NA KLUCZ OCZEKIWANY PRZEZ SERVER MCP ('lata_czlowieka')
        if name == "oblicz_wiek_psa":
            if "wiek" in args:
                value = args.pop("wiek")
                args["lata_czlowieka"] = value # Używamy klucza oczekiwanego przez serwer
                log_interaction("PATCH_MAPPING", f"Przemapowano klucz argumentu z 'wiek' na 'lata_czlowieka'. Nowe args: {args}")
        # ----------------------------------------------------------------------------

        log_interaction("TOOL_CALL", f"Model chce wywołać narzędzie: {name} z parametrami: {args}")
        
        # Nowa instancja klienta dla każdego wywołania 
        temp_client = Client(LOCAL_SERVER_ADDRESS_MCP)
        
        if self.is_connected and name in self.tool_names: 
            try:
                async with temp_client:
                    # ZMIANA: Przekazujemy argumenty jako PIERWSZY argument pozycyjny, 
                    # a NIE argumenty kluczowe (kwargs), co naprawia błąd Client.call_tool().
                    # FastMCP oczekuje słownika 'args' jako argumentu pozycyjnego.
                    result = await temp_client.call_tool(name, args)
                    
                    # FastMCP zwraca obiekt CallToolResult, musimy wydobyć treść
                    content_text = ""
                    if hasattr(result, 'content') and result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                content_text += content.text
                    else:
                        # Jeśli wynik nie jest listą content, po prostu używamy stringa
                        content_text = json.dumps(result) if isinstance(result, dict) else str(result)

                    log_interaction("TOOL_RESULT", f"Rezultat narzędzia {name}: {content_text}")
                    
                    # Zwracamy w formacie oczekiwanym przez Gemini
                    return {
                        "functionResponse": {
                            "name": name,
                            # Ważne: Wartość response musi być obiektem (słownikiem)
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
        
        # Ograniczenie historii
        if len(self.history) > MAX_HISTORY_LENGTH:
             self.history = self.history[-MAX_HISTORY_LENGTH:]
            
        self.history.append({"role": "user", "parts": [{"text": user_prompt}]})
        log_interaction("USER_PROMPT", user_prompt)
        
        # Używamy WYŁĄCZNIE narzędzi MCP, jeśli są połączone.
        # Jeśli nie są, używamy WYŁĄCZNIE Google Search.
        if self.is_connected:
             tools_to_use = self.tool_definitions
        else:
             # Użycie Google Search jako jedynego narzędzia (Grounding)
             tools_to_use = GOOGLE_SEARCH_TOOL
             
        payload = {
            "contents": self.history,
            "tools": tools_to_use, 
        }
        api_url_with_key = f"{GEMINI_API_URL}?key={API_KEY}"
        
        max_tool_turns = 5
        for turn in range(max_tool_turns):
            response = None
            
            # --- Pętla obsługi ponownych prób (Exponential Backoff) ---
            for attempt in range(MAX_RETRIES):
                try:
                    # Użycie asyncio.to_thread do wykonania blokującego requests.post w wątku
                    response = await asyncio.to_thread(
                        requests.post, api_url_with_key, json=payload, timeout=30
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    break
                
                except requests.exceptions.RequestException as e:
                    error_details = response.text if response is not None else "Brak odpowiedzi"
                    # Logowanie błędu, ale kontynuowanie próby
                    log_interaction("BŁĄD_REQUEST", f"Błąd komunikacji z Gemini API (próba {attempt+1}/{MAX_RETRIES}): {e}. Szczegóły: {error_details}")
                    if attempt < MAX_RETRIES - 1:
                        # Wycofanie wykładnicze
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        log_interaction("FATAL_ERROR", "Nie udało się skomunikować z Gemini API po wielu próbach.")
                        return
            
            # Jeśli result nie zostało ustawione po pętlach, kończymy
            if 'result' not in locals():
                 return
                 
            candidate = result.get("candidates", [{}])[0]
            content = candidate.get("content", {})
            
            function_calls_parts = [p for p in content.get("parts", []) if "functionCall" in p]
            
            if function_calls_parts:
                tool_calls_results = []
                
                # Wykonujemy wywołania narzędzi FastMCP
                for part in function_calls_parts:
                    function_call = part["functionCall"]
                    # Sprawdzamy, czy nazwa narzędzia jest w naszym zestawie
                    if function_call.get('name') in self.tool_names:
                        tool_results = await self.run_tool_call(function_call)
                        tool_calls_results.append(tool_results)
                    else:
                        error_msg = f"Model próbował wywołać nieznane narzędzie: {function_call.get('name')}. Użyto tylko narzędzi MCP w tej turze."
                        log_interaction("OSTRZEŻENIE_NARZĘDZIA", error_msg)
                        tool_calls_results.append({
                            "functionResponse": {
                                "name": function_call.get('name'),
                                "response": {"error": error_msg}
                            }
                        })

                # Dodajemy wywołanie narzędzia (model) i wynik narzędzia (tool) do historii
                self.history.append({"role": "model", "parts": function_calls_parts})
                if tool_calls_results:
                    self.history.append({"role": "tool", "parts": tool_calls_results})
                
                # Zaktualizowany payload do ponownego wywołania API z wynikami narzędzi
                payload["contents"] = self.history
                
                if turn == max_tool_turns - 1:
                    log_interaction("OSTRZEŻENIE", "Przekroczono limit tur na wywoływanie narzędzi.")
                    return 
            
            elif content.get("parts") and "text" in content["parts"][0]:
                # Ostateczna odpowiedź tekstowa z modelu
                model_response_text = content["parts"][0]["text"]
                self.history.append({"role": "model", "parts": [{"text": model_response_text}]})
                log_interaction("GEMINI_RESPONSE", model_response_text)
                return
            
            else:
                log_interaction("BŁĄD_API", "Nieoczekiwana, pusta odpowiedź z API. Cały wynik:\n" + json.dumps(result, indent=2))
                return

    async def async_run(self):
        """Asynchroniczna metoda uruchamiająca sesję."""
        await self.initialize_client()
        
        if not self.is_connected:
             print("\n--- BŁĄD: Brak połączenia z serwerem MCP. Narzędzia lokalne będą niedostępne. ---")
        else:
             tool_names_list = list(self.tool_names)
             print(f"\n--- Sukces: Dostępne narzędzia: {tool_names_list}. Google Search używane jako fallback. ---")
        
        print("\n--- Start Chatu ---")
        print("Wpisz 'koniec' aby zakończyć.")
        
        while True:
            try:
                # Blokujące wywołanie input() przeniesione do wątku
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
        # Użycie asyncio.run() do uruchomienia głównej pętli zdarzeń
        asyncio.run(host.async_run())
    except EnvironmentError as e:
        print(e)
        print("Upewnij się, że ustawiłeś zmienną środowiskową: export GEMINI_API_KEY='TWÓJ_KLUCZ'")
    except Exception as e:
        print(f"Błąd inicjalizacji: {e}")