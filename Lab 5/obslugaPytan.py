# obslugaPytan.py
# -*- coding: utf-8 -*-
"""
Skrypt:
- pobiera pytanie od użytkownika
- generuje embedding zapytania (Gemini / google.generativeai)
- odczytuje rekordy z tabeli WiedzaModelu (kolumny: Id, tekst, embedding)
  (embedding zapisany jako string "f1, f2, f3, ...")
- znajduje najbardziej podobny tekst (cosine similarity)
- przygotowuje prompt łączący pytanie, znaleziony tekst i polecenie:
  "Odpowiedz tylko na podstawie tego tekstu"
- zapisuje gotowy prompt oraz przykład "efektu RAG" do pliku efektRAG.txt,
  dołączając informacje z pliku luki.txt (zakres luki / opis)
"""

import os
import pyodbc
import json
from pathlib import Path
from typing import List, Optional, Tuple
import math

import google.generativeai as genai

# --- Konfiguracja (dostosuj ścieżki / connection string) ---
# Uwaga: nie zostawiaj klucza w kodzie — użyj zmiennej środowiskowej.
# Przykład ustawienia w systemie (Windows PowerShell):
# $env:GENAI_API_KEY="TWÓJ_KLUCZ"
genai.configure(api_key="AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs")

EMBEDDING_MODEL = "models/text-embedding-004"  # zgodnie z przygotujBaze.py

# Połączenie do MS SQL — zachowaj takie samo jak w przygotujBaze.py
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(localdb)\\MSSQLLocalDB;"
    "Database=lab 5;"
    "Integrated Security=True;"
)

# Pliki
LUKI_FILE = Path("luki.txt")
EFEKT_RAG_FILE = Path("efektRAG.txt")


# ------------------ Funkcje pomocnicze ------------------

def generuj_embedding_tekstu(tekst: str) -> Optional[List[float]]:
    """Generuje embedding dla zadanego tekstu (Gemini)."""
    if not tekst:
        return None
    try:
        resp = genai.embed_content(model=EMBEDDING_MODEL, content=tekst)
        # resp może być dict-like; zwróć listę floatów
        embedding = resp.get("embedding") if isinstance(resp, dict) else resp["embedding"]
        return embedding
    except Exception as e:
        print(f"❌ Błąd generowania embeddingu pytania: {e}")
        return None


def parsuj_embedding_z_bazy(embedding_str: str) -> List[float]:
    """Parsuje embedding zapisany jako '0.12, -0.3, ...' na listę floatów.
       Obsługuje puste / nieoczekiwane formaty - wtedy zwraca pustą listę."""
    if not embedding_str:
        return []
    try:
        # Usuń nawiasy, jeśli występują, oraz nadmiarowe spacje
        s = embedding_str.strip()
        s = s.strip("[]()")
        parts = [p.strip() for p in s.split(",") if p.strip() != ""]
        return [float(p) for p in parts]
    except Exception as e:
        print(f"⚠️ Nie udało się sparsować embeddingu: {e}. Zwracam pustą listę.")
        return []


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Oblicza podobieństwo kosinusowe między wektorami a i b.
       Jeśli jeden z wektorów jest pusty lub długości nie pasują, zwraca -1."""
    if not a or not b:
        return -1.0
    if len(a) != len(b):
        # Jeżeli długości różne, próbujemy uciąć do min lub zwracamy -1
        n = min(len(a), len(b))
        a = a[:n]
        b = b[:n]
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(x*x for x in b))
    if norm_a == 0 or norm_b == 0:
        return -1.0
    return dot / (norm_a * norm_b)


def pobierz_teksty_z_bazy(conn_str: str) -> List[Tuple[int, str, List[float]]]:
    """Pobiera wszystkie rekordy z tabeli WiedzaModelu i zwraca listę krotek:
       (Id, tekst, embedding_lista_float)."""
    wynik = []
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Id, tekst, embedding FROM WiedzaModelu")
            rows = cursor.fetchall()
            for row in rows:
                id_, tekst, emb_str = row[0], row[1] or "", row[2] or ""
                emb_list = parsuj_embedding_z_bazy(str(emb_str))
                wynik.append((id_, tekst.strip(), emb_list))
    except Exception as e:
        print(f"❌ Błąd podczas pobierania danych z bazy: {e}")
    return wynik


def znajdz_najblizszy(embedding_zapytania: List[float], rekordy: List[Tuple[int, str, List[float]]]) -> Optional[Tuple[int, str, float]]:
    """Zwraca (Id, tekst, similarity) najlepiej pasującego rekordu albo None."""
    najlepszy = None
    best_sim = -2.0
    for id_, tekst, emb in rekordy:
        sim = cosine_similarity(embedding_zapytania, emb)
        if sim > best_sim:
            best_sim = sim
            najlepszy = (id_, tekst, sim)
    return najlepszy


def przygotuj_prompt(pytanie: str, znaleziony_tekst: str) -> str:
    """Składa gotowy prompt dla modelu: pytanie + tekst + jasne polecenie korzystania wyłącznie z tekstu."""
    prompt = (
        "NIE ODPISUJ Z ZEWNĄTRZ — ODPOWIEDŹ TYLKO NA PODSTAWIE DOSTARCZONEGO TEKSTU.\n\n"
        "DOSTARCZONY TEKST (źródło z bazy WiedzaModelu):\n"
        "--------------------------------------------------------------------------------\n"
        f"{znaleziony_tekst}\n"
        "--------------------------------------------------------------------------------\n\n"
        "POLECENIE:\n"
        "Udziel konkretnej, zwięzłej odpowiedzi na poniższe pytanie, korzystając wyłącznie z informacji zawartych w dostarczonym tekście. "
        "Jeżeli pytanie wykracza poza informacje zawarte w tekście, wyraźnie napisz, że nie ma wystarczających danych w źródle.\n\n"
        "Pytanie:\n"
        f"{pytanie}\n\n"
        "ODPOWIEDŹ (tylko na podstawie powyższego tekstu):\n"
    )
    return prompt


def zapisz_efekt_rag(prompt: str, najlepszy_id: Optional[int], najlepszy_sim: Optional[float], luki_zawartosc: str, out_file: Path) -> None:
    """Zapisuje do pliku efektRAG.txt prompt, meta i przykładowy wpis 'model uzyskał wiedzę'."""
    try:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("=== PROMPT DLA MODELU (RAG) ===\n\n")
            f.write(prompt + "\n\n")
            f.write("=== META DLA RAG ===\n")
            f.write(f"Najlepiej pasujący rekord Id: {najlepszy_id}\n")
            f.write(f"Similarity (cosine): {najlepszy_sim}\n\n")
            f.write("=== ZAWARTOŚĆ PLIKU luki.txt (zakres/uwagi) ===\n")
            f.write(luki_zawartosc + "\n\n")
            f.write("=== PRZYKŁAD: EFEKT RAG ===\n")
            f.write("Model (przykład): Uzyskałem/uzyskałam wiedzę w zakresie opisanym w pliku luki.txt i "
                    "wykorzystałem wyłącznie tekst z bazy jako źródło informacji. "
                    "Jeśli brakowało informacji — wyraźnie to zaznaczono.\n")
        print(f"✅ Zapisano efekt RAG do pliku: {out_file.resolve()}")
    except Exception as e:
        print(f"❌ Błąd zapisu efektRAG: {e}")


# ------------------ Główna logika ------------------

def main():
    print("=== Obsługa pytań (RAG) ===")
    pytanie = input("Wpisz pytanie: ").strip()
    if not pytanie:
        print("❗ Nie podano pytania. Kończę.")
        return

    print("Generuję embedding zapytania...")
    emb_q = generuj_embedding_tekstu(pytanie)
    if emb_q is None:
        print("❌ Nie udało się wygenerować embeddingu zapytania. Kończę.")
        return

    print("Pobieram wpisy z bazy WiedzaModelu...")
    rekordy = pobierz_teksty_z_bazy(connection_string)
    if not rekordy:
        print("❌ Brak rekordów w bazie. Uzupełnij bazę (uruchom przygotujBaze.py) i spróbuj ponownie.")
        return

    print(f"Porównuję z {len(rekordy)} rekordami...")
    najlepszy = znajdz_najblizszy(emb_q, rekordy)
    if not najlepszy:
        print("❌ Nie znaleziono pasującego rekordu.")
        return

    najlepszy_id, najlepszy_tekst, najlepszy_sim = najlepszy
    print(f"✅ Najlepszy rekord Id={najlepszy_id}  (similarity={najlepszy_sim:.4f})")

    prompt = przygotuj_prompt(pytanie, najlepszy_tekst)

    # Wczytaj plik luki.txt, jeśli istnieje
    luki_zaw = ""
    if LUKI_FILE.exists():
        try:
            with open(LUKI_FILE, "r", encoding="utf-8") as f:
                luki_zaw = f.read()
        except Exception as e:
            luki_zaw = f"(błąd odczytu luki.txt: {e})"
    else:
        luki_zaw = "(Plik luki.txt nie istnieje — brak wykrytych zakresów.)"

    # Zapisz efekt RAG (prompt + meta + przykładowy wpis) do pliku efektRAG.txt
    zapisz_efekt_rag(prompt, najlepszy_id, najlepszy_sim, luki_zaw, EFEKT_RAG_FILE)

    

if __name__ == "__main__":
    main()
