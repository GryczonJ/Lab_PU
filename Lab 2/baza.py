# Proszę na Wikipedii wybrać sobie jakąś kategorię i podejrzeć jej zawartość.
# Proszę w oparciu o Visual Studio SQL Server Object Explorer utworzyć bazę danych
# Wikipedia z tabelką nazwaną zgodnie z nazwą kategorii. W tabeli mają być pola: klucz
# główny, hasło i treść. Wprowadź 3 przykładowe hasła.
# Proszę w Python stworzyć odpowiednią klasę Hasło z polami instancyjnymi Id, Hasło,
# Treść i metodą specjalną __str__.
# Proszę w Python utworzyć klasę zgodną z nazwą kategorii i z przedrostkiem Tabela_,
# która będzie miała 2 metody specjalne __enter__ i __exit__. W tych metodach proszę
# oprogramować automatycznie otwierane i zamykane połączenia z bazą na potrzeby
# konstrukcji with. Obiekt połączenia i kursor mają być przechowywane w polach
# instancyjnych. Klasa powinna udostępniać metodę instancyjną pobierz_hasła
# zwracającą listę obiektów klasy Hasło, metodę dodaj_hasło przyjmujących obiekt Hasło
# , metodę usuń_wszystko oraz metodę policz_hasła zwracającą liczbę haseł. Proszę
# zastosować Type Hints.
# Proszę, korzystając z nowej klasy Tabela_, dodać jedno własne przykładowe hasło i
# następnie pobierać wszystkie hasła z tabeli wyświetlając je na ekranie i zapisując po
# serializacji do pliku hasla.json.
# Zmodyfikować kod tak, że część testowa z powyższego akapitu będzie się wykonywać
# tylko przy bezpośrednim uruchomieniu skryptu (korzystając ze zmiennej __main__)
# W sprawozdaniu umieścić kod SQL tworzący bazę, program baza.py oraz wygenerowany
# plik json.

import pyodbc
import json
import jsonpickle
from typing import List

connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(localdb)\\MSSQLLocalDB;"
    "Database=Wikipedia;"
    "Integrated Security=True;"
)

class Hasło:
    def __init__(self, id: int | None, hasło: str, treść: str):
        """
            Inicjalizuje obiekt Hasło.
        """
        self.id = id
        self.hasło = hasło
        self.treść = treść

    def __str__(self):
        return f"Id: {self.id}, Hasło: {self.hasło}, Treść: {self.treść}"
    

class Tabela_Technika:
    def __init__(self, connection_string: str):
        """
        Inicjalizuje obiekt Tabela_Technika. 
        Przechowuje ciąg połączenia i inicjuje pola połączenia i kursora na None.
        """
        self.connection_string: str = connection_string
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            print("✅ Połączono automatycznie z bazą danych.")
        except Exception as e:
            self.conn = None
            self.cursor = None
            print(f"❌ Błąd połączenia: {e}")
        #self.conn: pyodbc.Connection | None = None
        #self.cursor: pyodbc.Cursor | None = None

    def __enter__(self) -> "Tabela_Technika":
        """Otwiera połączenie z bazą danych automatycznie przy użyciu 'with'."""
        self.conn = pyodbc.connect(self.connection_string)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Zamyka połączenie po zakończeniu bloku 'with'."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def pobierz_hasła(self) -> List[Hasło]:
        """Zwraca listę obiektów klasy Hasło z tabeli Technika."""
        self.cursor.execute("SELECT Id, hasło, treść FROM Technika")
        rows = self.cursor.fetchall()
        return [Hasło(id=row[0], hasło=row[1].strip(), treść=row[2].strip()) for row in rows]

    def dodaj_hasło(self, hasło: Hasło) -> None:
        """Dodaje nowe hasło do tabeli, obsługując duplikaty."""
        try:
            self.cursor.execute(
                "INSERT INTO Technika (hasło, treść) VALUES (?, ?)",
                (hasło.hasło, hasło.treść)
            )
            self.conn.commit()
        except pyodbc.IntegrityError:
            print(f"Błąd: Hasło o Id={hasło.Id} lub Hasło='{hasło.Hasło}' już istnieje. Rekord nie został dodany.")
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd podczas dodawania hasła: {e}")

    def usuń_wszystko(self) -> None:
        """Usuwa wszystkie rekordy z tabeli."""
        self.cursor.execute("DELETE FROM Technika")
        self.conn.commit()

    def policz_hasła(self) -> int:
        """Zwraca liczbę rekordów w tabeli."""
        self.cursor.execute("SELECT COUNT(*) FROM Technika")
        return self.cursor.fetchone()[0]
    
    def zapisz_do_json(self, nazwa_pliku: str = "hasla.json") -> None:
        """
        Serializuje wszystkie rekordy z tabeli Technika do pliku JSON.
        """
        try:
            hasla = self.pobierz_hasła()
            json_str = jsonpickle.encode(hasla, unpicklable=False)
            parsed = json.loads(json_str)

            with open(nazwa_pliku, "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)

            print(f"Zakończono pomyślnie. Plik '{nazwa_pliku}' został wygenerowany.")
        except Exception as e:
            print(f"BŁĄD: Wystąpił błąd podczas serializacji/zapisu do pliku: {e}")    


if __name__ == "__main__":
    
    nowe_hasło = Hasło(
        id=4, 
        hasło="Jan", 
        treść="Gryczon"
    )
    
    wszystkie_hasła: List[Hasło] = []
    
    try:
        
        with Tabela_Technika(connection_string) as tabela:
            print(f"--- Faza 1: Dodawanie hasła ---")
            tabela.dodaj_hasło(nowe_hasło)
            
            print(f"\n--- Faza 2: Pobieranie haseł ---")
            wszystkie_hasła = tabela.pobierz_hasła()

    except Exception as e:
        print(f"\nFATALNY BŁĄD: Nie udało się wykonać operacji na bazie danych: {e}")
        exit() 

    print("\n--- Faza 3: Wyświetlanie na ekranie ---")
    if wszystkie_hasła:
        print("Pobrane hasła z tabeli Technika:")
        for h in wszystkie_hasła:
            print(h)
    else:
        print("Nie znaleziono haseł w tabeli.")

    print(f"\n--- Faza 4: Serializacja do hasla.json ---")
    try:
        with Tabela_Technika(connection_string) as tabela:
            tabela.zapisz_do_json("hasla.json")
    except Exception as e:
        print(f"BŁĄD: Nie udało się otworzyć bazy danych do serializacji: {e}")