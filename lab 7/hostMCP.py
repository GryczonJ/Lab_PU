import os
import json
import logging
from fastmcp import ToolClient
from google import genai
from google.genai import types

# --- KONFIGURACJA ---
# 1. Konfiguracja logowania do pliku log.txt
LOG_FILE = "log.txt"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_FILE),
                        logging.StreamHandler()
                    ])

# 2. Ustawienia modelu Gemini
MODEL_NAME = "gemini-2.5-flash"
# Wymagany jest klucz API ustawiony jako zmienna środowiskowa!
# os.environ["GEMINI_API_KEY"] = "TWOJ_KLUCZ"
if not os.getenv("GEMINI_API_KEY"):
    logging.error("BŁĄD: Zmienna środowiskowa GEMINI_API_KEY nie jest ustawiona.")
    print("\nUSTAW KLUCZ API: Ustaw klucz Gemini API jako zmienną środowiskową 'GEMINI_API_KEY'.")

# 3. Konfiguracja Klienta MCP (dla serwera z Zadania 2)
# Upewnij się, że serwer serwerMCP_HTTP.py DZIAŁA na tym adresie!
MCP_SERVER_URL = "http://127.0.0.1:8000"
# --------------------

def main():
    """
    Główna funkcja aplikacji Host MCP.
    """
    logging.info("--- Uruchomienie aplikacji Host MCP ---")
    
    try:
        # Inicjalizacja klienta Gemini
        client = genai.Client()
        logging.info(f"Klient Gemini ({MODEL_NAME}) zainicjalizowany.")

        # Inicjalizacja klienta narzędzi MCP (Klient MCP)
        # FastMCP ToolClient pobierze definicje narzędzi z serwera HTTP SSE
        mcp_client = ToolClient(url=MCP_SERVER_URL)
        logging.info(f"Klient MCP zainicjalizowany. Pobieranie schematów z: {MCP_SERVER_URL}")

        # Pobranie schematów narzędzi, które zostaną przekazane do Gemini
        tool_schemas = mcp_client.get_schemas()
        
        if not tool_schemas:
            logging.warning("Brak narzędzi pobranych z serwera MCP.")
        else:
            logging.info(f"Pobrano {len(tool_schemas)} narzędzi dla Gemini.")
        
        # Inicjalizacja sesji czatu z narzędziami
        # Gemini przyjmuje schematy narzędzi w swojej własnej strukturze (types.Tool)
        
        # Konwersja schematów FastMCP/OpenAPI na format Gemini
        gemini_tools = [
            types.Tool.from_dict({
                "function_declarations": [schema.function_declaration]
            }) 
            for schema in tool_schemas
        ]
        
        # Używamy metody generate_content, aby móc obsłużyć wywołanie narzędzia w pętli
        chat_service = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                tools=gemini_tools
            )
        )
        logging.info("Sesja czatu z włączonymi narzędziami rozpoczęta.")

    except Exception as e:
        logging.error(f"Błąd inicjalizacji: {e}")
        return

    print("\n--- Rozpoczęcie konwersacji (Host MCP) ---")
    print(f"Model: {MODEL_NAME}. Narzędzia: {', '.join([s.name for s in tool_schemas])}")
    print("Wpisz 'wyjdz' lub 'exit' aby zakończyć.")
    print("-" * 50)

    # Główna pętla interakcji
    while True:
        user_prompt = input("Użytkownik > ").strip()
        
        if user_prompt.lower() in ["wyjdz", "exit"]:
            print("Zakończenie pracy Host MCP.")
            logging.info("Zakończenie pracy Host MCP przez użytkownika.")
            break

        if not user_prompt:
            continue

        # Logowanie pytania użytkownika
        logging.info(f"Pytanie użytkownika: {user_prompt}")
        
        # Wysyłanie pytania do modelu
        response = chat_service.send_message(user_prompt)
        
        # --- Pętla obsługi wywołań narzędzi (Host MCP jako Klient MCP) ---
        
        tool_calls = response.function_calls
        
        while tool_calls:
            print(f"🤖 Model proponuje użycie {len(tool_calls)} narzędzi...")
            logging.info(f"Model wywołał narzędzia: {[call.name for call in tool_calls]}")

            function_responses = []

            for call in tool_calls:
                function_name = call.name
                arguments = dict(call.args)
                
                # 1. Wywołanie narzędzia przez Klienta MCP
                try:
                    # mcp_client.call() wysyła żądanie do serwera serwerMCP_HTTP.py
                    tool_result = mcp_client.call(function_name, **arguments)
                    logging.info(f"Wynik narzędzia '{function_name}': {tool_result}")
                    print(f"✅ Wynik z narzędzia '{function_name}' ({arguments}): {tool_result}")

                    # 2. Tworzenie obiektu FunctionResponse
                    function_responses.append(
                        types.Part.from_function_response(
                            name=function_name, 
                            response={"result": tool_result}
                        )
                    )

                except Exception as e:
                    error_message = f"Błąd wykonania narzędzia '{function_name}': {e}"
                    logging.error(error_message)
                    print(f"❌ Błąd: {error_message}")
                    
                    # W przypadku błędu, również zwracamy informację do modelu
                    function_responses.append(
                        types.Part.from_function_response(
                            name=function_name, 
                            response={"error": error_message}
                        )
                    )

            # 3. Wysłanie wyników z powrotem do modelu
            response = chat_service.send_message(
                parts=function_responses
            )
            
            # Sprawdzenie, czy model chce użyć kolejnych narzędzi (rekurencyjnie)
            tool_calls = response.function_calls

        # --- Koniec obsługi narzędzi ---

        # Wypisanie ostatecznej odpowiedzi modelu
        model_answer = response.text
        print(f"Gemini > {model_answer}")
        
        # Logowanie odpowiedzi modelu
        logging.info(f"Odpowiedź modelu: {model_answer}")
        print("-" * 50)


if __name__ == "__main__":
    main()