import datetime
import requests
import os
import json
import time 

from google import genai
from google.genai import types
from bs4 import BeautifulSoup

# Zmienna symulująca klucz API
API_KEY = "AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs" 

# STAŁE DLA MECHANIZMU PONAWIANIA Z WYKŁADNICZYM OPÓŹNIENIEM
MAX_RETRIES = 5       
INITIAL_DELAY = 2     

# INSTRUKCJA SYSTEMOWA DLA MODELU (Uzupełniona o drugą część logiki)
SYSTEM_INSTRUCTION = (
    "Jesteś inteligentnym asystentem internetowym. "
    "Zawsze staraj się użyć narzędzia 'ZnajdzStrony', gdy potrzebujesz informacji zewnętrznych. "
    "Jeśli wyniki z 'ZnajdzStrony' są puste, spróbuj ponownie, używając krótszego, bardziej ogólnego hasła, "
    "Zawsze dąż do uzyskania co najmniej jednego wyniku URL, a następnie wywołaj 'PobierzStrone' dla pierwszego najbardziej relewantnego URL-a."
    "Po uzyskaniu HTML, podsumuj najważniejsze informacje w swojej odpowiedzi. "
)

# ----------------------------------------------------
# Funkcje narzędziowe, które model może wywołać
# ----------------------------------------------------

def ZnajdzStrony(haslo: str):
    """Wyszukuje strony poprzez scraping wyników wyszukiwarki DuckDuckGo HTML.

    Args:
        haslo: Słowo kluczowe do wyszukania.

    Returns:
        Lista słowników z polami 'url' i 'opis'.
    """
    print(f"DEBUG: Wywołano ZnajdzStrony z hasłem: '{haslo}'")

    url = "https://duckduckgo.com/html/"
    params = {"q": haslo}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.7,en;q=0.6",
    }

    try:
        r = requests.get(url, params=params, timeout=10, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"BŁĄD podczas pobierania wyników: {e}")
        return [{"url": "", "opis": f"Błąd połączenia: {e}"}]

    soup = BeautifulSoup(r.text, "html.parser")

    wyniki = []
    # Selektor CSS dla wyników wyszukiwania DuckDuckGo HTML
    for a in soup.select("a.result__url"):
        link = a.get("href", "")
        # Próba znalezienia opisu w sąsiednim elemencie, jeśli dostępny
        opis_element = a.find_next_sibling(attrs={"class": "result__snippet"})
        opis = opis_element.get_text(strip=True) if opis_element else a.get_text(strip=True)

        if link:
            wyniki.append({
                "url": link,
                "opis": opis
            })

    # Jeśli nic nie znaleziono — zwróć pustą listę
    if not wyniki:
        print("DEBUG: Brak wyników – HTML scraping nie znalazł wyników.")
        return []

    return wyniki[:5]


def PobierzStrone(url: str, max_chars: int = 3000):
    """Pobiera stronę i zwraca oczyszczony tekst do modelu."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, timeout=15, headers=headers)
        r.raise_for_status()

        # Parsowanie HTML
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Usuwamy skrypty i style
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Pobieramy widoczny tekst
        text = soup.get_text(separator="\n")
        text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        
        # Ograniczamy długość
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return {"text": text}

    except requests.exceptions.RequestException as e:
        return {"text": f"Błąd podczas pobierania strony: {e}"}
    except Exception as e:
        return {"text": f"Nieznany błąd: {e}"}


# def PobierzStrone(url: str):
#     """Pobiera HTML strony pod wskazanym URL.

#     Args:
#         url: Pełny adres URL strony do pobrania.

#     Returns:
#         Słownik zawierający pole 'html' z zawartością strony.
#     """
#     print(f"DEBUG: Wywołano PobierzStrone dla URL: '{url}'")
#     try:
#         # Ustawienie nagłówka User-Agent
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#         r = requests.get(url, timeout=15, headers=headers)
#         r.raise_for_status()
        
#         # Zwracamy tylko fragment, aby nie zaśmiecać logów
#         content_snippet = r.text[:2000] + "..."
#         return {"html": content_snippet}
        
#     except requests.exceptions.RequestException as e:
#         print(f"BŁĄD POBIERANIA STRONY: {e}")
#         return {"html": f"Błąd podczas pobierania strony: {e}"}
#     except Exception as e:
#         return {"html": f"Nieznany błąd: {e}"}


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
            # POPRAWIONY OPIS PODKREŚLAJĄCY KONIECZNOŚĆ KRÓTKIEGO HASŁA
            description=(
                "Wyszukuje strony poprzez scraping wyników DuckDuckGo HTML. Zwraca listę obiektów z polami 'url' i 'opis'. "
                "Unikaj zbyt precyzyjnych fraz, które mogą zwrócić pustą listę."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "haslo": types.Schema(type=types.Type.STRING, description="Krótkie, ogólne hasło kluczowe do wyszukania.")
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
    Uruchamia model Gemini z lub bez Function Calling i zapisuje całą komunikację,
    używając Exponential Backoff dla odporności na błędy API.
    """
    
    # 1. Inicjalizacja klienta
    try:
        client = genai.Client(api_key=api_key) 
    except Exception as e:
        print(f"BŁĄD: Nie można zainicjować klienta Gemini. {e}")
        return

    # Konfiguracja: ustawienie narzędzi, oraz dodanie instrukcji systemowej
    config = types.GenerateContentConfig(
        tools=TOOL_SCHEMAS if use_function_calling else [],
        system_instruction=SYSTEM_INSTRUCTION if use_function_calling else None 
    )
    
    log = []
    log.append(f"=== TEST: {'Z Function Calling' if use_function_calling else 'ORYGINALNY SYSTEM'} ===")
    log.append(f"Data/Czas: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(f"Pytanie Użytkownika: {prompt}")
    
    # Inicjalizacja pełnej historii konwersacji (tylko z promptem użytkownika)
    full_conversation_history = [
        types.Content(role='user', parts=[types.Part.from_text(text=prompt)])
    ]
    
    # Maksymalnie 5 "turnusów" z modelem
    for turnus_number in range(MAX_RETRIES): 
        
        # 1. WYWOŁANIE MODELU
        current_response = None
        for attempt in range(MAX_RETRIES):
            try:
                # Wysłanie CAŁEJ HISTORII
                current_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_conversation_history,
                    config=config,
                )
                log.append(f"Sukces w turnusie {turnus_number + 1} po próbie: {attempt + 1}")
                break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_DELAY * (2 ** attempt)
                    log.append(f"BŁĄD Wywołania API (Turnus {turnus_number + 1}, Próba {attempt + 1}): {e}")
                    log.append(f"Aplikuję Wykładnicze Opóźnienie. Oczekiwanie {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    log.append(f"BŁĄD Wywołania API (OSTATNIA próba {attempt + 1}): {e}")
                    with open(file_name, 'a', encoding='utf-8') as f: f.write('\n'.join(log))
                    return

        if not current_response:
            break
            
        log.append(f"\n--- Odpowiedź Modelu ({turnus_number + 1}. Wywołanie) ---")
        log.append(f"Tekst: {safe_text(current_response)}")

        # Dodanie odpowiedzi modelu do pełnej historii konwersacji
        full_conversation_history.append(types.Content(role='model', parts=current_response.parts))
        
        # 2. KONIEC (Model odpowiada tekstem i nie ma żądań FC)
        if not use_function_calling or not current_response.function_calls:
            if turnus_number > 0:
                log.append("Model zakończył pracę, generując odpowiedź tekstową.")
            break 
            
        # 3. LOGIKA FUNCTION CALLING
        tool_results = []
        search_failed = False
        log.append("\nModel poprosił o wywołanie funkcji:")
        
        for function_call in current_response.function_calls:
            func_name = function_call.name
            func_args = dict(function_call.args)
            
            log.append(f"  - FUNKCJA: {func_name}, ARGUMENTY: {func_args}")
            
            if func_name in AVAILABLE_TOOLS:
                function_to_call = AVAILABLE_TOOLS[func_name]
                
                try:
                    # WYKONANIE FUNKCJI
                    result = function_to_call(**func_args)
                    log.append(f"  - WYNIK: Sukces. Zapisano wynik.")
                    result_preview = json.dumps(result, ensure_ascii=False, indent=2)
                    log.append(f"  - ZAWARTOSC WYNIKU (skrót): {result_preview[:500]}...")

                    # Sprawdzenie, czy ZnajdzStrony zwróciło pustą listę
                    if func_name == "ZnajdzStrony" and isinstance(result, list) and not result:
                        search_failed = True
                        
                except Exception as e:
                    result = {"result": f"Błąd wykonania funkcji {func_name}: {e}"}
                    log.append(f"  - BŁĄD WYKONANIA: {e}")
                
                tool_results.append(
                    types.Content(
                        role='tool', 
                        parts=[
                            types.Part.from_function_response(
                                name=func_name,
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

        # Dodanie wyników narzędzi do pełnej historii konwersacji
        full_conversation_history.extend(tool_results)
        
        # 4. PRZYGOTOWANIE DO PONOWNEJ PRÓBY (Jeśli wyszukiwanie się nie powiodło)
        if search_failed:
             log.append("DEBUG: WYSZUKIWANIE NIEUDANE (Pusta Lista Wyników). Wymuszam ponowne wywołanie modelu (Turnus: Wymuszone Ponowne Wyszukanie).")
             # Dodajemy do historii sztuczny prompt użytkownika, który ponawia żądanie.
             full_conversation_history.append(
                 types.Content(role='user', parts=[types.Part.from_text(text="Wyniki wyszukiwania dla poprzedniego hasła były puste. Proszę o ponowną próbę, używając krótszego, bardziej ogólnego hasła, zgodnie z instrukcją systemową.")])
             )
    
    # 5. Zapisanie logu do pliku
    log.append("================================================\n")
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
    user_prompt ="opisz wydział inżynieria materiałowa i cyfryzacjia przemysłu na politechnika śląska poszukaj aktualnych informacji na stronach" 
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
    if not wyniki:
        print("Brak wyników – lista 'wyniki' jest pusta.\n")
    else:
        for i, w in enumerate(wyniki, start=1):
            print(f"{i}. URL: {w['url']}")
            print(f"   Opis: {w['opis']}\n")

    print("=== TEST: PobierzStrone ===")
    for w in wyniki:
        if not w["url"]:
            continue
        print(f"Pobieram: {w['url']}")
        html = PobierzStrone(w["url"])
        print("Fragment HTML:")
        print(html["html"][:500])  # tylko pierwsze 500 znaków
        print("\n---\n")

if __name__ == "__main__":
    PrzeprowadzTestyGemini()