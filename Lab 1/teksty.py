# Opis: Stwórz moduł teksty.py, który zawiera funkcje:
#      policz_słowa(tekst) – zwraca liczbę słów,
#      unikalne_słowa(tekst) – zwraca zbiór unikalnych słów,
#      czy_zawiera(tekst, słowo) – zwraca wartość logiczną.

def policz_słowa(tekst: str) -> int:
    """Funkcja zwraca liczbę słów w podanym tekście."""
    słowa = tekst.split()
    return len(słowa)

def unikalne_słowa(tekst: str) -> set[str]:
    """Funkcja zwraca zbiór unikalnych słów w podanym tekście."""
    słowa = tekst.split()
    return set(słowa)

def czy_zawiera(tekst: str, słowo: str) -> bool:
    """Funkcja sprawdza, czy podane słowo znajduje się w tekście."""
    return słowo in tekst