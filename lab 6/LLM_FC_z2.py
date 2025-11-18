import datetime
import requests
import os
import json
from google import genai
from google.genai import types

# Zmienna symulująca klucz API
API_KEY = "AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs" 

# ----------------------------------------------------
# Funkcje narzędziowe, które model może wywołać
# ----------------------------------------------------

def ZnajdzStrony(haslo: str):
    """Wyszukuje strony w DuckDuckGo API.

    Args:
        haslo: Słowo kluczowe do wyszukania.

    Returns:
        Lista słowników z polami 'url' i 'opis'.
    """
    print(f"DEBUG: Wywołano ZnajdzStrony z hasłem: '{haslo}'")
    url = "https://api.duckduckgo.com/"
    params = {
        "q": haslo,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status() # Rzuć wyjątek dla złych statusów HTTP
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"BŁĄD ZAPYTANIA DuckDuckGo: {e}")
        return [{"url": "", "opis": f"Błąd połączenia z API DuckDuckGo: {e}"}]
    except json.JSONDecodeError:
        print("BŁĄD: Niepoprawna odpowiedź JSON z DuckDuckGo.")
        return [{"url": "", "opis": "Niepoprawna odpowiedź JSON z API."}]

    wyniki = []

    # DuckDuckGo korzysta z list 'RelatedTopics'
    for item in data.get("RelatedTopics", []):
        if "FirstURL" in item and "Text" in item:
            wyniki.append({
                "url": item["FirstURL"],
                "opis": item["Text"]
            })
        # czasem wchodzą podlisty
        if "Topics" in item:
            for t in item["Topics"]:
                if "FirstURL" in t and "Text" in t:
                    wyniki.append({
                        "url": t["FirstURL"],
                        "opis": t["Text"]
                    })

    # Dodaj wynik głównego zapytania
    if data.get("AbstractURL") and data.get("AbstractText"):
        wyniki.insert(0, {
            "url": data["AbstractURL"],
            "opis": data["AbstractText"]
        })
    
    # Ogranicz liczbę wyników dla czytelności logu
    return wyniki[:5]


def PobierzStrone(url: str):
    """Pobiera HTML strony pod wskazanym URL.

    Args:
        url: Pełny adres URL strony do pobrania.

    Returns:
        Słownik zawierający pole 'html' z zawartością strony.
    """
    print(f"DEBUG: Wywołano PobierzStrone dla URL: '{url}'")
    try:
        # Ustawienie nagłówka User-Agent, aby niektóre strony nas nie blokowały
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        r = requests.get(url, timeout=15, headers=headers)
        r.raise_for_status()
        
        # Zwracamy tylko fragment, aby nie zaśmiecać logów
        content_snippet = r.text[:2000] + "..."
        return {"html": content_snippet}
        
    except requests.exceptions.RequestException as e:
        print(f"BŁĄD POBIERANIA STRONY: {e}")
        return {"html": f"Błąd podczas pobierania strony: {e}"}
    except Exception as e:
        return {"html": f"Nieznany błąd: {e}"}


# Lista dostępnych funkcji dla Function Calling
AVAILABLE_TOOLS = {
    "ZnajdzStrony": ZnajdzStrony,
    "PobierzStrone": PobierzStrone,
}

# Definicje narzędzi w formacie zrozumiałym dla API Gemini
TOOL_SCHEMAS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="ZnajdzStrony",
            description="Wyszukuje strony pasujące do hasła, używając darmowego API DuckDuckGo. Zwraca listę obiektów z polami url i opis. Używaj tej funkcji jako pierwszego kroku, aby znaleźć docelowy URL.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "haslo": types.Schema(type=types.Type.STRING, description="Hasło kluczowe do wyszukania.")
                },
                required=["haslo"]
            ),
        ),
        types.FunctionDeclaration(
            name="PobierzStrone",
            description="Pobiera HTML wskazanej strony internetowej. Używaj tylko po udanym wywołaniu ZnajdzStrony, aby pobrać konkretną stronę.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "url": types.Schema(type=types.Type.STRING, description="Pełny i poprawny URL strony do pobrania.")
                },
                required=["url"]
            ),
        )
    ])
]

# Funkcja pomocnicza do bezpiecznego wydobywania tekstu
def safe_text(response):
    """Zwraca tekst z odpowiedzi modelu, lub placeholder."""
    return response.text if response.text else "[Brak tekstu w odpowiedzi]"


def run_model_test(
    file_name: str, 
    prompt: str, 
    use_function_calling: bool = False,
    api_key: str = API_KEY 
):
    """
    Uruchamia model Gemini z lub bez Function Calling i zapisuje całą komunikację.
    """
    
    # 1. Inicjalizacja klienta
    try:
        # Prawdziwy klient jest inicjalizowany tutaj, ale w środowisku
        # developerskim klucz API może nie być wymagany/dostępny.
        # Zostawiamy tę logikę, aby zachować zgodność z API.
        client = genai.Client(api_key=api_key) 
    except Exception as e:
        print(f"BŁĄD: Nie można zainicjować klienta Gemini. {e}")
        return

    # Konfiguracja: ustawienie narzędzi (lub pustej listy)
    config = types.GenerateContentConfig(
        tools=TOOL_SCHEMAS if use_function_calling else []
    )
    
    log = []
    log.append(f"=== TEST: {'Z Function Calling' if use_function_calling else 'ORYGINALNY SYSTEM'} ===")
    log.append(f"Data/Czas: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(f"Pytanie Użytkownika: {prompt}")
    
    # 1. WYWOŁANIE MODELU
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=config,
        )
    except Exception as e:
        log.append(f"BŁĄD Wywołania API (1. Wywołanie): {e}")
        with open(file_name, 'a', encoding='utf-8') as f: f.write('\n'.join(log))
        return


    log.append(f"\n--- Odpowiedź Modelu (1. Wywołanie) ---")
    log.append(f"Tekst: {safe_text(response)}")
    
    # 2. LOGIKA FUNCTION CALLING (Tylko jeśli jest włączona)
    if use_function_calling and response.function_calls:
        
        tool_results = []
        log.append("\nModel poprosił o wywołanie funkcji:")
        
        for function_call in response.function_calls:
            func_name = function_call.name
            func_args = dict(function_call.args)
            
            log.append(f"  - FUNKCJA: {func_name}, ARGUMENTY: {func_args}")
            
            if func_name in AVAILABLE_TOOLS:
                function_to_call = AVAILABLE_TOOLS[func_name]
                
                # WYKONANIE FUNKCJI
                try:
                    result = function_to_call(**func_args)
                    log.append(f"  - WYNIK: Sukces. Zapisano wynik.")
                    log.append(f"  - ZAWARTOSC WYNIKU: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
                except Exception as e:
                    result = {"result": f"Błąd wykonania funkcji {func_name}: {e}"}
                    log.append(f"  - BŁĄD WYKONANIA: {e}")
                
                tool_results.append(
                    types.Content(
                        role='tool', 
                        parts=[
                            types.Part.from_function_response(
                                name=func_name,
                                # WAŻNE: W API Google GenAI należy używać obiektu JSON, 
                                # a nie tylko surowej wartości, np. {'result': wynik_funkcji}
                                response={'result': result} 
                            )
                        ]
                    )
                )
            else:
                log.append(f"BŁĄD: Nieznana funkcja: {func_name}")
                tool_results.append(
                     types.Content(
                        role='tool', 
                        parts=[
                            types.Part.from_function_response(
                                name=func_name,
                                response={'result': f"BŁĄD: Nieznana funkcja: {func_name}"} 
                            )
                        ]
                    )
                )

        # 3. Wysłanie wyników z powrotem do modelu (Drugi turnus)
        log.append("\n--- DRUGIE WYWOŁANIE MODELU (Z WYNIKAMI FUNKCJI) ---")
        
        # Budowanie pełnego kontekstu rozmowy
        conversation_history = [
            #types.Content(role='user', parts=[types.Part.from_text(prompt)]),
            types.Content(role='user', parts=[types.Part.from_text(text=prompt)]),
            types.Content(role='model', parts=response.parts) # Pierwsza odpowiedź modelu (żądanie funkcji)
        ] + tool_results # Wyniki wywołania funkcji (z roli 'tool')
        
        try:
            second_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=conversation_history,
                config=config,
            )
            log.append(f"Odpowiedź Modelu (2. Wywołanie):")
            log.append(f"Tekst: {safe_text(second_response)}")
        except Exception as e:
            log.append(f"BŁĄD Wywołania API (2. Wywołanie): {e}")

    elif use_function_calling:
        log.append("\nModel nie poprosił o wywołanie funkcji w pierwszym turnusie.")
            
    log.append("================================================\n")
    
    # Zapisanie logu do pliku
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write('\n'.join(log))


def PrzeprowadzTestyGemini():
    """
    Uruchamia testy modelu Gemini w trybie oryginalnym i Function Calling 
    i zapisuje logi do logOrg_z2.txt i logFC_z2.txt.
    """
    # Usuń stare pliki log, jeśli istnieją
    if os.path.exists("logOrg_z2.txt"): os.remove("logOrg_z2.txt")
    if os.path.exists("logFC_z2.txt"): os.remove("logFC_z2.txt")
    
    # Prompt wymagający wieloetapowej interakcji (szukanie -> pobieranie -> podsumowanie)
    user_prompt ="Znajdź stronę główną gry 'Pokemon Legends: Z-A' i wypisz trzy główne cechy/funkcje rozgrywki (features) wymienione na stronie. Zwróć tylko nagłówki tych cech w formie listy punktowanej." # "Znajdź stronę główną portalu 'Pokemony' i podsumuj trzy pierwsze nagłówki artykułów widocznych na stronie. Zwróć tylko nagłówki."
    print(f"Użyty prompt: {user_prompt}")
    
    # --- 1. TEST SYSTEMU ORYGINALNEGO ---
   
    print("\n--- 1. Testowanie: System Oryginalny (logOrg_z2.txt) ---")
    run_model_test(
        file_name="logOrg_z2.txt",
        prompt=user_prompt,
        use_function_calling=False
    )
    print("Zapisano log do logOrg_z2.txt")
    
    # --- 2. TEST SYSTEMU Z FUNCTION CALLING ---
    print("\n--- 2. Testowanie: System z Function Calling (logFC_z2.txt) ---")
    run_model_test(
        file_name="logFC_z2.txt",
        prompt=user_prompt,
        use_function_calling=True
    )
    print("Zapisano log do logFC_z2.txt")

    print("\n✅ Ukończono. Proszę sprawdzić pliki logOrg_z2.txt i logFC_z2.txt w celu weryfikacji.")

def Testuj():
    print("=== TEST: ZnajdzStrony ===")
    haslo = input("Podaj hasło do wyszukania: ")
    wyniki = ZnajdzStrony(haslo)

    print("\nZnalezione wyniki:")
    for i, w in enumerate(wyniki, start=1):
        print(f"{i}. URL: {w['url']}")
        print(f"   Opis: {w['opis']}\n")

    print("=== TEST: PobierzStrone ===")
    for w in wyniki:
        if not w["url"]:
            continue
        print(f"Pobieram: {w['url']}")
        html = PobierzStrone(w["url"])
        print("Fragment HTML:")
        print(html["html"][:500])   # tylko pierwsze 500 znaków
        print("\n---\n")

if __name__ == "__main__":
    #x=ZnajdzStrony("Pokemon Legends")
    #print(x[0]["url"])
    #print(PobierzStrone(x[0]["url"]))
    Testuj()
    # To wywołanie musi być zmienione na lokalne, aby używało zdefiniowanych tu funkcji
    #PrzeprowadzTestyGemini()
     