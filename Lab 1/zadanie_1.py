# Zadanie 1: Kalkulator logiczno-matematyczny
# Napisz program, który:
#  pobiera od użytkownika dwie liczby całkowite,
#  wykonuje operacje: dodawanie, odejmowanie, mnożenie, dzielenie,
#  sprawdza, czy liczby są równe, czy jedna jest większa od drugiej,
#  wyświetla wynik w formacie: „Liczba A jest większa/mniejsza/równa liczbie B”. 
try:
    a = float(input("Podaj liczbę a:"))
    b = float(input("Podaj liczbę b: "))
except ValueError:
    print("To nie jest liczba")
    exit()

print("Wynik dodawania")
print (f"{a} + {b} = {(a+b):.2f}")

print("Wynik odejmowanie")
print (f"{a} - {b} = {(a-b):.2f}")

print("Wynik mnożenie")
print (f"{a} * {b} = {(a*b):.2f}")

if (b != 0):
    x=a/b
    print("Wynik dzielenie")
    print (f"{a} / {b} = {(a/b):.2f}")
else: print("Holero nie dzielimy przez zero")

if a > b:
    print("podane a > b")
    print(f"{a:.2f} jest większe od {b:.2f}")
elif a < b:
    print("podane a < b")
    print(f"{a:.2f} jest mniejsze od {b:.2f}")
else: print(f"są sobie równe  ;) {a:.2f} == {b:.2f}")

