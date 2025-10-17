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
