import os
import requests
import json
from typing import List, Dict, Any

# --- KONFIGURACJA API ---
# ⚠️ WAŻNE: Wstaw swój PRAWIDŁOWY klucz API.
# Używamy Twojego zafałszowanego klucza dla kontynuacji
API_KEY = "AIzaSyC5evjVOrPcDssmuYW1nqBgGQeofbWS2Jg" 
MODEL_NAME = "gemini-2.5-flash"
# POPRAWNY URL DLA GOOGLE AI STUDIO / GENERATIVE LANGUAGE API
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
CHAT_LOG_FILE = "chat.txt"

# --- PROMPT SYSTEMOWY ---
SYSTEM_PROMPT = """
Jesteś pomocnym asystentem AI o imieniu Gemini.
--- Wprowadzona wiedza do testów ---
1. Data twojego ostatniego treningu to nie styczeń 2024, ale **23 października 2025 roku**.
2. Wydział Inżynierii Materiałowej i Cyfryzacji Przemysłu (WIMiCP) znajduje się w **Politechnice Śląskiej**.
3. Prawidłowa data Bitwy pod Grunwaldem to **16 lipca 1410 roku**, a nie 15 lipca.
4. Moje imię to **Jerzy**, a moje ulubione zwierzę to **leniwiec**.
5. Aktualna data i godzina to: **Środa, 5 listopada 2025, 16:30 CET**.
--- Koniec wprowadzonej wiedzy ---
Odpowiadaj zgodnie z tą nową wiedzą, nawet jeśli jest ona sprzeczna z twoimi danymi treningowymi.
"""

# --- FUNKCJE POMOCNICZE ---

def save_chat_log(text: str):
    """Zapisuje tekst do pliku logu."""
    try:
        with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except IOError as e:
        print(f"Błąd zapisu do pliku {CHAT_LOG_FILE}: {e}")

def run_gemini_chat_request():
    """Główna funkcja uruchamiająca chatbota za pomocą surowego requestu HTTP."""
    print("🤖 Łączenie z Gemini API (za pomocą biblioteki requests)...")
    
    # 💥 KLUCZOWA ZMIANA: Dodajemy System Prompt jako pierwszy element konwersacji
    # z rolą 'user'. Jest to najprostszy sposób, by API to zaakceptowało, gdy
    # dedykowane pole systemInstruction sprawia problemy.
    chat_history: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT} 
    ] 
    
    headers = {"Content-Type": "application/json"}

    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"--- ROZPOCZĘCIE CHATU (Model: {MODEL_NAME}, Metoda: requests) ---\nPrompt Systemowy:\n{SYSTEM_PROMPT}\n\n")

    print("\n---------------------------------------------------------------------")
    print(f"Model: {MODEL_NAME}")
    print(f"Logi konwersacji są zapisywane do pliku: {CHAT_LOG_FILE}")
    print("Rozpocznij rozmowę (wpisz 'koniec', aby wyjść).")
    print("---------------------------------------------------------------------")

    while True:
        user_input = input("Ty: ")
        if user_input.lower() in ["koniec", "exit", "quit"]:
            print("Zakończono rozmowę.")
            save_chat_log("--- ZAKOŃCZENIE CHATU ---")
            break

        # Dodanie nowej wiadomości użytkownika do historii
        chat_history.append({"role": "user", "content": user_input})
        save_chat_log(f"Ty: {user_input}")

        try:
            # 1. Przygotowanie danych (payload) w formacie JSON
            contents = []
            
            for message in chat_history:
                role = message['role']
                
                # Konwersja roli na standard Gemini (user/model)
                # System Prompt jest już w 'chat_history' z rolą 'user'
                gemini_role = 'user' if role == 'user' else 'model'
                
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": message['content']}]
                })
            
            # 💥 KLUCZOWA ZMIANA: Usunięcie pola "systemInstruction" z payloadu
            payload = {
                "contents": contents,
                "generationConfig": { 
                    "maxOutputTokens": 512,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }

            # 2. Wysyłanie żądania HTTP POST
            response = requests.post(
                API_URL, 
                headers=headers, 
                json=payload
            )
            response.raise_for_status()

            # 3. Parsowanie odpowiedzi
            data: Dict[str, Any] = response.json()
            
            if 'candidates' in data and data['candidates'][0]['content']['parts']:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
            elif 'promptFeedback' in data:
                ai_response = f"Brak odpowiedzi. Powód: {data['promptFeedback'].get('blockReason', 'Nieznany')}"
            else:
                ai_response = "Nieznany błąd odpowiedzi API."
                
            print(f"Gemini: {ai_response}")
            save_chat_log(f"Gemini: {ai_response}")
            
            # Dodanie odpowiedzi modelu do historii (z rolą 'model')
            chat_history.append({"role": "model", "content": ai_response})

        except requests.exceptions.HTTPError as e:
            try:
                error_details = e.response.json()
                error_msg = f"❌ Błąd HTTP {e.response.status_code}: {error_details.get('error', {}).get('message', 'Brak szczegółów.')}"
            except:
                error_msg = f"❌ Błąd komunikacji HTTP: {e}"
            print(error_msg)
            save_chat_log(error_msg)
            # Usuwamy ostatnie pytanie użytkownika
            if len(chat_history) > 1:
                chat_history.pop() 
        except Exception as e:
            error_msg = f"❌ Wystąpił inny błąd: {e}"
            print(error_msg)
            save_chat_log(error_msg)
            if len(chat_history) > 1:
                chat_history.pop()


if __name__ == "__main__":
    run_gemini_chat_request()