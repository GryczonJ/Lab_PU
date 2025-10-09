# Zadanie 1: Kalkulator logiczno-matematyczny
# Napisz program, który:
#  pobiera od użytkownika dwie liczby całkowite,
#  wykonuje operacje: dodawanie, odejmowanie, mnożenie, dzielenie,
#  sprawdza, czy liczby są równe, czy jedna jest większa od drugiej,
#  wyświetla wynik w formacie: „Liczba A jest większa/mniejsza/równa liczbie B”. 

a = int(input("Podaj liczbę a:"))
b = int(input("Podaj liczbę b:"))
#print(f"{liczba:.2f}")

print("Wynik dodawania")
print (f"{a} + {b} = {(a+b):.2f}")

print("Wynik odejmowanie")
print (f"{a} - {b} = {a-b}")

print("Wynik mnożenie")
print (f"{a} * {b} = {a*b}")

if (b != 0):
    x=a/b
    print("Wynik dzielenie")
    print (f"{a} / {b} = {round(x,2)}")
else: print("Holero nie dzielimy przez zero")

if a > b:
    print("podane a > b")
    print(f"{a} jest większe od {b}")
elif a < b:
    print("podane a < b")
    print(f"{a} jest mniejsze od {b}")
else: print(f"są sobie równe  ;) {a} == {b}")

