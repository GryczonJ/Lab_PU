# add_initial_data.py
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Movie

def add_data():
    db: Session = SessionLocal()
    try:
        # Sprawdzenie, czy dane już istnieją
        if db.query(Movie).count() == 0:
            movies_to_add = [
                Movie(tytul="Blade Runner 2049", gatunek="Sci-Fi", dostepny_do_wypozyczenia=True, ile_egzemplarzy=3),
                Movie(tytul="Fight Club", gatunek="Dramat", dostepny_do_wypozyczenia=True, ile_egzemplarzy=2),
                Movie(tytul="Parasite", gatunek="Thriller", dostepny_do_wypozyczenia=False, ile_egzemplarzy=1),
            ]
            db.add_all(movies_to_add)
            db.commit()
            print("Początkowe rekordy zostały dodane.")
        else:
            print("Tabela już zawiera dane, pomijam dodawanie początkowych rekordów.")
    except Exception as e:
        print(f"Wystąpił błąd podczas dodawania danych: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_data()