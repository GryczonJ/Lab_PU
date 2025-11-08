# testdb.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Importowanie modelu i Base (zakładamy, że mymodel.py jest w tym samym katalogu)
# WAŻNE: Wymaga, aby w mymodel.py był zdefiniowany Base
from mymodel import Base, Ksiazka 

# 2. Konfiguracja bazy danych
# Użyjemy SQLite. Zmień ten adres, jeśli używasz innej bazy (np. PostgreSQL/MySQL)
DATABASE_URL = "mssql+pyodbc://@(localdb)\MSSQLLocalDB/Biblioteka?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(DATABASE_URL)

# Upewnienie się, że tabela 'ksiazki' istnieje
# Jeśli baza danych nie istnieje, zostanie utworzona. 
# Jeśli tabela 'ksiazki' nie istnieje, zostanie utworzona.
Base.metadata.create_all(bind=engine)

# 3. Tworzenie sesji
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def dodaj_ksiazke():
    """Funkcja dodająca nową książkę do bazy danych."""
    
    # Tworzenie instancji sesji
    session = SessionLocal()
    
    try:
        # 4. Tworzenie obiektu Ksiazka
        nowa_ksiazka = Ksiazka(
            # Pola obowiązkowe
            title="Python for Data Science",
            summary="Comprehensive guide to Python libraries like Pandas and NumPy for data analysis.",
            # Opcjonalne pola (jeśli zostały dodane, np. polski_tytul=...)
            # Możesz je pominąć, ponieważ są nullable=True
            polskie_streszczenie= None
        )

        # 5. Dodanie obiektu do sesji
        session.add(nowa_ksiazka)
        
        # 6. Zatwierdzenie zmian w bazie danych
        session.commit()
        
        # Opcjonalnie: odświeżenie obiektu, aby uzyskać nadane ID
        session.refresh(nowa_ksiazka)

        print(f"✅ Książka dodana pomyślnie. ID: {nowa_ksiazka.id}, Tytuł: '{nowa_ksiazka.title}'")

    except Exception as e:
        session.rollback() # Wycofanie transakcji w razie błędu
        print(f"❌ Wystąpił błąd podczas dodawania książki: {e}")
        
    finally:
        session.close() # Zamknięcie sesji

def dodaj_wiele_ksiazek(ksiazki_dane: list[Ksiazka]):
    """
    Dodaje wiele książek do bazy danych.
    Parametr:
        ksiazki_dane: lista obiektów Ksiazka do dodania.
    """
    session = SessionLocal()
    dodane = 0

    try:
        for ksiazka in ksiazki_dane:
            # Sprawdzenie, czy książka o takim tytule już istnieje
            istnieje = session.query(Ksiazka).filter_by(title=ksiazka.title).first()
            if istnieje:
                print(f"⚠️ Książka '{ksiazka.title}' już istnieje — pominięto.")
                continue

            # Dodanie obiektu otrzymanego jako parametr
            session.add(ksiazka)
            print(f"➕ Dodano książkę: '{ksiazka.title}', streszczenie: {ksiazka.summary[:10]}...")
            dodane += 1

        session.commit()
        print(f"✅ Dodano {dodane} książek do bazy (lub pominięto duplikaty).")

    except Exception as e:
        session.rollback()
        print(f"❌ Wystąpił błąd podczas dodawania książek: {e}")

    finally:
        session.close()

if __name__ == "__main__":
    dodaj_ksiazke()