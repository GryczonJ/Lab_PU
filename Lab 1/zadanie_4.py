# Zadanie 4: Analizator tekstu – liczba słów i unikalnych wyrazów

# apisz skrypt, który:
#      importuje moduł,
#      pobiera tekst od użytkownika,
#      wyświetla analizę tekstu. 

import teksty as txt

tekst = input("podaj tekst: ")

print("Liczba słów w podanym tekście: ", txt.policz_słowa(tekst))
print("Unikalne słowa w podanym tekście: ", txt.unikalne_słowa(tekst))
slowo = input("Podaj słowo do sprawdzenia czy występuje w tekście: ")
if txt.czy_zawiera(tekst, slowo):
    print(f"Podany tekst zawiera słowo: {slowo}")
else: print(f"Podany tekst nie zawiera słowa: {slowo}")