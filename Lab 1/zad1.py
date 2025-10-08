# Zadanie 1: Kalkulator logiczno-matematyczny 
# Napisz program, który: 
#  pobiera od użytkownika dwie liczby całkowite, 
#  wykonuje operacje: dodawanie, odejmowanie, mnożenie, dzielenie, 
#  sprawdza, czy liczby są równe, czy jedna jest większa od drugiej, 
#  wyświetla wynik w formacie: „Liczba A jest większa/mniejsza/równa liczbie B”


# Pobieranie liczb od użytkownika
a = int(input("Podaj pierwszą liczbę całkowitą: "))
b = int(input("Podaj drugą liczbę całkowitą: "))

# Operacje matematyczne
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
if b != 0:
    print(f"{a} / {b} = {a / b}")
else:
    print("Nie można dzielić przez zero.")

# Porównanie liczb
if a > b:
    print(f"Liczba {a} jest większa od liczby {b}.")
elif a < b:
    print(f"Liczba {a} jest mniejsza od liczby {b}.")
else:
    print(f"Liczba {a} jest równa liczbie {b}.")
