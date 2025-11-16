#przygotujBaze.py
# W pliku przygotujBaze.py opierając na zadaniu 3 w laboratorium 2 korzstając np. zWikipedii utwórz bazę tekstów angielskich uzpełniających wiedzę modelu i zapisanychtabeli MS SQL z kolumnami id, tekst, embedding.
# Dla każdego teksu wygeneruj w kolumnie embedding wektor go opisujacy w formaciejson (przy pomocy Gemini API).

import pyodbc
import json
import jsonpickle
from typing import List, Optional
from pathlib import Path  
import hashlib

import requests as req
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
import time
import google.generativeai as genai 


# UWAGA: Ten klucz jest publiczny, usuń go i użyj zmiennej środowiskowej
genai.configure(api_key="AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs")

# UŻYTY MODEL EMBEDDINGOWY
MODEL_NAME = "models/text-embedding-004" 
EMBEDDING_MODEL = "models/text-embedding-004" 

BASE_URL = 'https://pl.wikipedia.org'
URL = f'{BASE_URL}/wiki/Kategoria:Technika'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# --- Konfiguracja ścieżek ---
# Główna ścieżka projektu (podana przez użytkownika)
BASE_PATH = Path("D:/konda/envs/lab-pu/Lab_PU/Lab 5")
# Docelowy folder na pliki JSON (wiedza modelu)
TARGET_FOLDER = BASE_PATH / "wiedza_modelu"
# Domyślna nazwa pliku JSON
DEFAULT_JSON_FILE = "baza_wiedzy.json"


# Ciąg połączenia - ZACHOWANY 1:1
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(localdb)\\MSSQLLocalDB;"
    "Database=lab 5;"
    "Integrated Security=True;"
)

class Tekst:
    """
    Klasa reprezentująca pojedynczy tekst uzupełniający wiedzę z jej embeddingiem.
    """
    def __init__(self, id: Optional[int], tekst: str, embedding: str):
        self.id = id
        self.tekst = tekst
        self.embedding = embedding

    def __str__(self) -> str:
        skrocony_tekst = self.tekst[:50] + "..." if len(self.tekst) > 50 else self.tekst
        skrocony_embedding = self.embedding[:20] + "..." if len(self.embedding) > 20 else self.embedding
        return f"Id: {self.id}, Tekst: '{skrocony_tekst}', Embedding: '{skrocony_embedding}'"
    

class Tabela_WiedzaModelu:
    """
    Klasa do zarządzania tabelą WiedzaModelu. Sposób łączenia jest zachowany 1:1.
    """
    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            print("✅ Połączono automatycznie z bazą danych (w __init__).")
        except Exception as e:
            self.conn = None
            self.cursor = None
            print(f"❌ Błąd połączenia w __init__: {e}")

    def __enter__(self) -> "Tabela_WiedzaModelu":
        self.conn = pyodbc.connect(self.connection_string)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def pobierz_teksty(self) -> List[Tekst]:
        if not self.cursor:
            return []
        self.cursor.execute("SELECT Id, tekst, embedding FROM WiedzaModelu")
        rows = self.cursor.fetchall()
        return [Tekst(id=row[0], tekst=row[1].strip(), embedding=row[2].strip()) for row in rows]

    def dodaj_tekst(self, tekst: Tekst) -> None:
        """
        Dodaje nowy tekst i embedding do tabeli WiedzaModelu, 
        sprawdzając wcześniej, czy rekord o danej treści (tekst) już istnieje.
        Wymaga użycia CONVERT, aby poprawnie porównać typ TEXT z parametrem NVARCHAR.
        """
        if not self.cursor or not self.conn:
            print("Błąd: Brak aktywnego kursora lub połączenia.")
            return
            
        try:
            # 1. Sprawdzenie, czy rekord już istnieje, używając CONVERT(NVARCHAR(MAX), ...)
            # Jest to niezbędne, aby porównać kolumnę TEXT z parametrem (NVARCHAR)
            self.cursor.execute(
                "SELECT COUNT(*) FROM WiedzaModelu WHERE CONVERT(NVARCHAR(MAX), tekst) = ?",
                (tekst.tekst,)
            )
            count = self.cursor.fetchone()[0]

            if count > 0:
                # Rekord istnieje
                print(f"⚠️ Pomięto dodawanie. Rekord z tekstem '{tekst.tekst[:30]}...' już istnieje w bazie danych.")
                return

            # 2. Dodawanie nowego rekordu (INSERT)
            # INSERT jest kompatybilny, więc nie wymaga konwersji
            self.cursor.execute(
                "INSERT INTO WiedzaModelu (tekst, embedding) VALUES (?, ?)",
                (tekst.tekst, tekst.embedding)
            )
            self.conn.commit()
            print(f"✅ Dodano nowy tekst: '{tekst.tekst[:30]}...'")
            
        except Exception as e:
            # Wystąpił błąd bazy danych podczas zapytania lub wstawiania
            print(f"❌ Wystąpił błąd podczas operacji na bazie danych: {e}")

    def pobierz_wszystkie_teksty(self) -> List[Tekst]:
        teksty: List[Tekst] = []
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                # Zamiast 'pobierz_wszystkie_teksty' używamy standardowego selecta
                cursor.execute("SELECT Id, tekst, embedding FROM WiedzaModelu")
                rows = cursor.fetchall()
                for row in rows:
                    teksty.append(Tekst(id=row[0], tekst=row[1].strip(), embedding=row[2].strip()))
            print(f"✅ Pomyślnie wczytano {len(teksty)} rekordów z bazy danych.")
        except Exception as e:
            print(f"❌ Błąd połączenia lub pobierania danych: {e}")
        return teksty
    
    def zapisz_do_json(self, target_folder: Path, nazwa_pliku: str) -> None:
        """
        Serializuje wszystkie rekordy do pliku JSON w określonym folderze.
        """
        if not self.cursor:
            print("Błąd: Brak aktywnego połączenia z bazą danych do serializacji.")
            return

        try:
            # 1. Tworzenie folderu docelowego, jeśli nie istnieje
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # 2. Konstruowanie pełnej ścieżki pliku
            full_path = target_folder / nazwa_pliku
            
            # 3. Serializacja i zapis
            teksty = self.pobierz_teksty()
            json_str = jsonpickle.encode(teksty, unpicklable=False)
            parsed = json.loads(json_str)

            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)

            print(f"💾 Zakończono pomyślnie. Plik został wygenerowany pod ścieżką: '{full_path}'")
        except Exception as e:
            print(f"❌ BŁĄD: Wystąpił błąd podczas serializacji/zapisu do pliku: {e}")

def generuj_embedding(tekst: str) -> Optional[List[float]]:
    """Generuje wektor embedding dla podanego tekstu za pomocą modelu Gemini."""
    if not tekst: return None
    try:
        # Maksymalna długość wejściowa dla text-embedding-004 to 2048 tokenów
        response = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=tekst
        )
        # response.embedding to lista float
        
        return response['embedding']
    # except APIError as e:
    #     print(f"❌ Błąd API Gemini: {e}")
    #     return None
    
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd podczas generowania embeddingu: {e}")
        return None

# --- Funkcje Scrappingowe (Nie zmienione) ---

def pobierz_liste_hasel(url):
    res = req.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = bs(res.text, 'html.parser')
    items = []
    # Używamy Link i Tekst jako kluczy, zgodnie z nowym schematem
    for a in soup.select('#mw-pages ul li a'):
        items.append({'Tekst': a.text, 'Link': BASE_URL + a['href'], 'Treść': ''})
    return pd.DataFrame(items)

def czysc_tekst(html):
    soup = bs(html, 'html.parser')
    content = soup.find("div", class_="mw-content-ltr mw-parser-output")
    if not content: return ""
    for tag in content(['table', 'sup', 'style', 'script']): tag.decompose()
    text = ' '.join(p.get_text() for p in content.find_all('p', recursive=False))
    text = re.sub(r'\[\d+|\[[a-z]\]', '', text)
    # Ograniczenie tekstu, aby nie przekroczyć limitu tokenów (ok. 1000 słów)
    return re.sub(r'\s+', ' ', text).strip()[:8000]


def main_scraper():
    print("--- ROZPOCZĘCIE SKRAPOWANIA I GENEROWANIA EMBEDDINGÓW ---")
    
    df = pobierz_liste_hasel(URL)
    print(f"Znaleziono {len(df)} haseł do przetworzenia.")
    
    # Użycie konstrukcji with do automatycznego zarządzania połączeniem z bazą
    try:
        with Tabela_WiedzaModelu(connection_string) as tabela:
            
            for i, row in df.iterrows():
                haslo_nazwa = row['Tekst']
                haslo_link = row['Link']

                # 1. Sprawdzanie duplikatu w bazie przed pobieraniem (Opcjonalne, ale efektywne)
                # Używamy prostego zapytania SELECT COUNT, które zostało wcześniej ustalone
                try:
                    tabela.cursor.execute(
                        "SELECT COUNT(*) FROM WiedzaModelu WHERE CONVERT(NVARCHAR(MAX), tekst) LIKE ?",
                        (haslo_nazwa,) # Sprawdzamy, czy hasło o tej nazwie już zostało zapisane
                    )
                    if tabela.cursor.fetchone()[0] > 0:
                        print(f"⚠️ Pomięto: '{haslo_nazwa}' już istnieje (lub jest podobne) w bazie.")
                        continue
                except Exception as e:
                    print(f"❌ Błąd sprawdzenia duplikatu: {e}. Kontynuuję bez kontroli.")
                
                print(f"Pobieranie i embeddowanie: {haslo_nazwa}...")
                
                try:
                    # 2. Pobranie i czyszczenie treści
                    r = req.get(haslo_link, headers=HEADERS, timeout=15)
                    r.raise_for_status()
                    tresc = czysc_tekst(r.text)
                    
                    if not tresc:
                        print("Pominięto: Treść jest pusta.")
                        continue
                        
                    # 3. Generowanie embeddingu
                    embedding_vector = generuj_embedding(tresc)
                    
                    if embedding_vector is None:
                        print("Pominięto: Nie udało się wygenerować embeddingu.")
                        continue
                        
                    # 4. Zapis do bazy danych
                    # Konwersja wektora (lista float) na string (tekst)
                    embedding_str = ", ".join(map(str, embedding_vector))
                    
                    nowy_tekst = Tekst(id=None, tekst=tresc, embedding=embedding_str)
                    tabela.dodaj_tekst(nowy_tekst)
                    
                except Exception as e:
                    print(f"Błąd krytyczny przy '{haslo_nazwa}': {e}")
                
                time.sleep(1) # Czekaj, by nie obciążać Wikipedii

        # 5. Serializacja na koniec
        with Tabela_WiedzaModelu(connection_string) as tabela:
            tabela.zapisz_do_json(TARGET_FOLDER, DEFAULT_JSON_FILE)
            
        print("\n--- Zakończono proces skrapowania, embeddowania i zapisu. ---")
            
    except Exception as e:
        print(f"\n🛑 FATALNY BŁĄD: Nie udało się otworzyć bazy danych: {e}")


if __name__ == "__main__":
    # Uruchomienie głównego skryptu pobierania i embeddowania
    main_scraper()

    print(f"🚀 Rozpoczęcie testu. Ścieżka docelowa JSON: {TARGET_FOLDER}")
    
    # Utworzenie listy tekstów do dodania
    nowe_teksty: List[Tekst] = [
        Tekst(
            id=None, 
            tekst="Model Transformer (uwaga) zrewolucjonizował przetwarzanie języka naturalnego (NLP).", 
            embedding="0.77, -0.33, 0.11, 0.99, -0.21" 
        ),
        Tekst(
            id=None,
            tekst="Huta Katowice to duży kombinat metalurgiczny, który znajduje się w Dąbrowie Górniczej.",
            # Przykładowy embedding dla nowej informacji
            embedding="0.91, -0.05, 0.44, 0.62, -0.78"
        )
    ]
    
    wszystkie_teksty: List[Tekst] = []
    
    try:
        with Tabela_WiedzaModelu(connection_string) as tabela:
            print(f"\n--- Faza 1: Dodawanie tekstów ---")
            
            # Pętla dodająca wszystkie nowe obiekty z listy
            for tekst in nowe_teksty:
                tabela.dodaj_tekst(tekst)
            
            print(f"\n--- Faza 2: Pobieranie tekstów ---")
            wszystkie_teksty = tabela.pobierz_teksty()

    except Exception as e:
        print(f"\n🛑 FATALNY BŁĄD: Nie udało się wykonać operacji na bazie danych: {e}")
        exit() 

    print("\n--- Faza 3: Wyświetlanie na ekranie ---")
    if wszystkie_teksty:
        print("Pobrane rekordy:")
        for t in wszystkie_teksty:
            print(t)
    else:
        print("Nie znaleziono rekordów w tabeli.")

    print(f"\n--- Faza 4: Serializacja do folderu {TARGET_FOLDER.name} ---")
    try:
        with Tabela_WiedzaModelu(connection_string) as tabela:
            # Wywołanie z nowymi parametrami
            tabela.zapisz_do_json(TARGET_FOLDER, DEFAULT_JSON_FILE)
    except Exception as e:
        print(f"❌ BŁĄD: Nie udało się otworzyć bazy danych do serializacji: {e}")