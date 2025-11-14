# Stwórz konto w serwisie https://huggingface.co, potwierdź użytkownika przez email oraz
# pobierz i zapisz trwale na kolejne zajęcia token typu write.
# W pliku testLLM.py połącz się z modelem Qwen/Qwen3-235B-A22B i poprzez odpowiedni
# prompt poleć mu przetłumaczenie jednego, przykładowego streszczenia książki na język
# polski. Zadbaj o to, żeby podawał czyste tłumaczenie, bez własnych komentarzy. Wynik
# wyświetl na ekranie.
# Dodaj do modelu Ksiazka pole polskie_streszczenie (nullable), utwórz migrację
# DodaniePolaPolskieStreszczenie i zaktualizuj bazę danych.
# Następnie pliku tłumaczenieLLM.py dla wszystkich książek już znajdujących w bazie
# danych przetłumacz ich streszczenia na język polski wypełniając pola
# polskie_streszczenie.
# Sprawozdanie: testLM.py, migracja DodaniePolaPolskieStreszczenie.py,
# tłumaczenieLLM.py. 

import os
import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

# -----------------
# Konfiguracja Bazy Danych
# -----------------
from mymodel import Base, Ksiazka 
DATABASE_URL = os.getenv("DATABASE_URL")
 
engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def tłumacz(text_to_translate: str) -> str | None:
    """Wysyła zapytanie o tłumaczenie do modelu LLM."""

    if not text_to_translate or text_to_translate.strip() == "Brak streszczenia dostępnego.":
        return None
    
    PROMPT_TŁUMACZENIA = (
            "Przetłumacz poniższe streszczenie na język polski. Podaj wyłącznie czyste tłumaczenie, bez żadnych dodatkowych komentarzy ani wstępu:\n\n"
            f"{text_to_translate}"
        )
    try:
        response = query({
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT_TŁUMACZENIA 
                    }
                ]
            }
        ],
        "model": "Qwen/Qwen3-VL-235B-A22B-Instruct:novita"
        })
   
        # Poprawiona obsługa błędu w przypadku braku 'choices'
        if "choices" not in response or not response["choices"]:
            print(f"   ❌ Błąd API: Brak odpowiedzi. Pełna odpowiedź: {response}")
            return None

        # Tłumaczenie
        translated_text = response["choices"][0]["message"]["content"]
        return translated_text.strip() # Usuwamy białe znaki na początku/końcu
    
    except (KeyError, IndexError) as e:
        print(f"   ❌ Ogólny błąd podczas zapytania do LLM: {e}")
        # print("Pełna odpowiedź dla debugowania:")
        # print(response)
        return None

    
def tlumacz_i_aktualizuj_baze():
    """Pobiera książki, tłumaczy i aktualizuje pole polskie_streszczenie."""
    session = SessionLocal()
    
    try:
        # Znajdź książki, dla których brakuje tłumaczenia
        ksiazki = session.query(Ksiazka).filter(Ksiazka.polskie_streszczenie == None).all()
        
        if not ksiazki:
            print("Wszystkie książki mają już przetłumaczone streszczenia lub baza jest pusta. ✅")
            return

        print(f"Znaleziono {len(ksiazki)} książek do przetłumaczenia.")
        
        for ksiazka in ksiazki:
            print(f"\n-> Przetwarzanie: {ksiazka.title} (ID: {ksiazka.id})")
            
            # Tłumaczenie
            tlumaczenie = tłumacz(ksiazka.summary)
            
            if tlumaczenie:
                ksiazka.polskie_streszczenie = tlumaczenie
                print(ksiazka.polskie_streszczenie)
                session.add(ksiazka)
                print(f"   ✅ Zaktualizowano streszczenie.")
            else:
                print(f"   ❌ Nie udało się przetłumaczyć dla książki {ksiazka.id}.")
        
        session.commit()
        print("\n=== Proces tłumaczenia i zapisu zakończony. ===")
        
    except Exception as e:
        session.rollback()
        print(f"\n🚨 Błąd podczas operacji na bazie danych: {e}")
        
    finally:
        session.close()

if __name__ == "__main__":
    tlumacz_i_aktualizuj_baze()