import datetime
import requests
import os
import json

from google import genai
from google.genai import types

# ----------------------------------------------------
# KLUCZ API (Przekazywany bezpośrednio do klienta)
# ----------------------------------------------------
# W celach demonstracyjnych, klucz jest zdefiniowany jako stała.
# W środowisku produkcyjnym zaleca się użycie os.environ['GEMINI_API_KEY']
API_KEY = "AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs" 

# ----------------------------------------------------
# 1. DEFINICJE NARZĘDZI (FUNCTION CALLING)
# ----------------------------------------------------

# def safe_text(resp):
#     return resp.text.strip() if getattr(resp, "text", None) else "(Brak tekstu – model zwrócił function_call)"
def safe_text(resp):
    """Zwraca tekst z odpowiedzi Gemini, jeśli istnieje."""
    try:
        if resp and resp.text:
            return resp.text.strip()
        return "(Brak tekstu – model zwrócił wywołanie funkcji)"
    except:
        return "(Brak tekstu – wyjątek przy odczycie)"

def PobierzDateCzas():
    """Zwraca aktualną datę i czas w formacie tekstowym."""
    teraz = datetime.datetime.now()
    format_daty = "%Y-%m-%d %H:%M:%S"
    return teraz.strftime(format_daty)

# ---

def PobierzCeneBitcoina():
    """Pobiera aktualną cenę Bitcoina w USD z zewnętrznego API (CoinGecko)."""
    api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(api_url)
        response.raise_for_status() 
        dane = response.json()
        cena = dane.get('bitcoin', {}).get('usd')
        return cena if cena is not None else "Nie udało się znaleźć ceny Bitcoina."
    except requests.exceptions.RequestException as e:
        return f"Błąd połączenia z API: {e}"

# Lista dostępnych funkcji dla Function Calling
AVAILABLE_TOOLS = {
    "PobierzDateCzas": PobierzDateCzas,
    "PobierzCeneBitcoina": PobierzCeneBitcoina,
}

# Definicje narzędzi w formacie zrozumiałym dla API Gemini
TOOL_SCHEMAS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="PobierzDateCzas",
            description="Zwraca aktualną datę i czas w formacie tekstowym.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={}),
        ),
        types.FunctionDeclaration(
            name="PobierzCeneBitcoina",
            description="Pobiera aktualną cenę Bitcoina w USD z zewnętrznego API.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={}),
        ),
    ])
]

# ----------------------------------------------------
# 2. FUNKCJA OBSŁUGUJĄCA LOGIKĘ I LOGOWANIE
# ----------------------------------------------------
def run_original_model_test(file_name: str, prompt: str):
    """
    Uruchamia model Gemini bez Function Calling i zapisuje całą komunikację
    do pliku logowania.
    
    :param file_name: Nazwa pliku logowania (np. logOrg.txt).
    :param prompt: Pytanie użytkownika.
    """
    
    try:
        # Klient inicjalizuje się, szukając klucza w zmiennych środowiskowych
        # Jeśli klucz nie jest ustawiony, konieczne będzie przekazanie go jawnie:
        # client = genai.Client(api_key="TWÓJ_KLUCZ")
        client = genai.Client() 
    except Exception as e:
        print(f"BŁĄD: Nie można zainicjować klienta Gemini. Upewnij się, że klucz API jest ustawiony. Szczegóły: {e}")
        return

    # Konfiguracja: ustawienie pustej listy narzędzi
    config = types.GenerateContentConfig(tools=[])
    
    log = []
    
    log.append("=== TEST: ORYGINALNY SYSTEM (Dowód braku aktualnej wiedzy) ===")
    log.append(f"Pytanie Użytkownika: {prompt}")
    
    # 1. WYWOŁANIE MODELU
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=config,
        )
        
        log.append(f"Odpowiedź Modelu (1. Wywołanie):")
        
        # Dodanie informacji o odpowiedzi
        if safe_text(response):
            log.append(f"Tekst: {safe_text(response)}")
        else:
            log.append("Brak tekstu w odpowiedzi. Możliwy błąd serwera.")
            
    except Exception as e:
        log.append(f"BŁĄD API: Wystąpił błąd podczas komunikacji z API: {e}")

    log.append("================================================\n")
            
    # Zapisanie logu do pliku
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write('\n'.join(log))


def run_model_test(
    file_name: str, 
    prompt: str, 
    use_function_calling: bool = False,
    api_key: str = API_KEY  # Dodanie klucza jako argumentu
):
    """
    Uruchamia model Gemini z lub bez Function Calling i zapisuje całą komunikację.
    """
    
    try:
        # Inicjalizacja klienta z kluczem API
        client = genai.Client(api_key=api_key) 
    except Exception as e:
        print(f"BŁĄD: Nie można zainicjować klienta Gemini. Upewnij się, że klucz API jest poprawny. {e}")
        return

    # Konfiguracja: ustawienie narzędzi (lub pustej listy)
    config = types.GenerateContentConfig(
        tools=TOOL_SCHEMAS if use_function_calling else []
    )
    
    log = []
    log.append(f"=== TEST: {'Z Function Calling' if use_function_calling else 'ORYGINALNY SYSTEM'} ===")
    log.append(f"Pytanie Użytkownika: {prompt}")
    
    # 1. WYWOŁANIE MODELU
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt],
        config=config,
    )
    
    log.append(f"Odpowiedź Modelu (1. Wywołanie):")
    log.append(f"Tekst: {safe_text(response)}")
    
    # 2. LOGIKA FUNCTION CALLING (Tylko jeśli jest włączona)
    if use_function_calling:
        if response.function_calls:
            log.append("Model poprosił o wywołanie funkcji:")
            
            tool_results = []
            
            for function_call in response.function_calls:
                func_name = function_call.name
                func_args = dict(function_call.args)
                
                log.append(f"  - Funkcja: {func_name}, Argumenty: {func_args}")
                
                if func_name in AVAILABLE_TOOLS:
                    function_to_call = AVAILABLE_TOOLS[func_name]
                    result = function_to_call(**func_args)
                    
                    log.append(f"  - Wynik Wywołania: {result}")
                    
                    tool_results.append(
                        types.Part.from_function_response(
                            name=func_name,
                            response={'result': result}
                        )
                    )
                else:
                    log.append(f"BŁĄD: Nieznana funkcja: {func_name}")
            
            # Wysłanie wyników z powrotem do modelu
            second_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, types.Content(role='model', parts=response.parts), types.Content(role='tool', parts=tool_results)],
                config=config,
            )
            
            log.append(f"Odpowiedź Modelu (2. Wywołanie po FC):")
            log.append(f"Tekst: {safe_text(second_response)}")
            
        else:
            log.append("Model nie poprosił o wywołanie funkcji.")
            
    log.append("================================================\n")
            
    # Zapisanie logu do pliku
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write('\n'.join(log))



# ----------------------------------------------------
# 3. GŁÓWNA CZĘŚĆ APLIKACJI
# ----------------------------------------------------

def TestujFunkcjePomocnicze():
    """
    Testuje i wyświetla wyniki funkcji PobierzDateCzas i PobierzCeneBitcoina.
    """
    print("--- Testowanie Funkcji Pomocniczych (Poza Gemini) ---")
    
    aktualny_czas = PobierzDateCzas()
    print(f"Aktualna data i czas: {aktualny_czas}")

    aktualna_cena = PobierzCeneBitcoina()
    if isinstance(aktualna_cena, (int, float)):
        print(f"Aktualna cena Bitcoina: {aktualna_cena:.2f} USD")
    else:
        print(f"Aktualna cena Bitcoina: {aktualna_cena}")
    
    print("\n--- Rozpoczęcie Testów Gemini ---")

def PrzeprowadzTestyGemini():
    """
    Uruchamia testy modelu Gemini w trybie oryginalnym i Function Calling 
    i zapisuje logi do logOrg.txt i logFC.txt.
    """
    # Usuń stare pliki log, jeśli istnieją
    if os.path.exists("logOrg.txt"): os.remove("logOrg.txt")
    if os.path.exists("logFC.txt"): os.remove("logFC.txt")
    
    user_prompt = "Jaki jest aktualny czas i jaka jest aktualna cena Bitcoina?"
    
    # --- 1. TEST SYSTEMU ORYGINALNEGO ---
    print("--- 1. Testowanie: System Oryginalny (logOrg.txt) ---")
    run_model_test(
        file_name="logOrg.txt",
        prompt=user_prompt,
        use_function_calling=False
    )
    print("Zapisano log do logOrg.txt")

    # --- 2. TEST SYSTEMU Z FUNCTION CALLING ---
    print("\n--- 2. Testowanie: System z Function Calling (logFC.txt) ---")
    run_model_test(
        file_name="logFC.txt",
        prompt=user_prompt,
        use_function_calling=True
    )
    print("Zapisano log do logFC.txt")

    print("\n✅ Ukończono. Proszę sprawdzić pliki logOrg.txt i logFC.txt w celu weryfikacji.")

if __name__ == "__main__":
    PrzeprowadzTestyGemini()
    #TestujFunkcjePomocnicze()