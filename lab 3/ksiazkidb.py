import string
import requests
import  testdb
from mymodel import Base, Ksiazka 
API_URL = "https://gutendex.com/books/"
LICZBA_STRON = 1  # każda strona = 32 książki

def pobierz_ksiazki() -> list[Ksiazka]:
    """Pobiera książki z API Gutendex i zwraca listę obiektów Ksiazka."""
    wszystkie_ksiazki = []
    
    for page in range(1, LICZBA_STRON + 1):
        try:
            response = requests.get(API_URL, params={"page": page})
            data = response.json()
            books = data.get("results", [])
            print(f"✅ Pobrano stronę {page} ({len(books)} książek).")
            
            # Konwersja słowników na obiekty Ksiazka
            for book in books:
                title = book.get("title", "Brak tytułu")
                summary = book.get("summaries") or "Brak streszczenia dostępnego."
                
                ksiazka_obj = Ksiazka(
                    title=title,
                    summary=summary[0] if summary else summary,
                    polskie_streszczenie=None
                )
                wszystkie_ksiazki.append(ksiazka_obj)
            
        except Exception as e:
            print(f"❌ Błąd podczas pobierania strony {page}: {e}")

    print(f"\n📚 Łącznie pobrano {len(wszystkie_ksiazki)} książek.\n")
    return wszystkie_ksiazki         

def wyświetl_przykladowe_ksiazki(wszystkie_ksiazki: list[Ksiazka]) -> None:
    """Wyświetla kilka przykładowych książek z pobranych danych."""
    for i, book in enumerate(wszystkie_ksiazki[:10], 1):
        print(f"{i}. {book.title}")
        print(f"   {book.summary}\n")

if __name__ == "__main__":
    wszystkie_ksiazki = pobierz_ksiazki()
    #wyświetl_przykladowe_ksiazki(wszystkie_ksiazki)  
    testdb.dodaj_wiele_ksiazek(wszystkie_ksiazki)
