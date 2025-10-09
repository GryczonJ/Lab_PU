# Zadanie 3: Praca z zbiorami
# Stwórz program, który:
#  pobiera dwie listy zakupów od dwóch osób,
#  konwertuje je na zbiory,
#  wyświetla:
#     o wspólne produkty (część wspólna),
#     o produkty unikalne dla każdej osoby (różnica),
#     o pełną listę produktów (suma zbiorów).

# from typeguard import typechecked

#@typechecked
def wczytanie():
    zakupy = input("Podaj produktow: ")
    string_list = zakupy.split(',')

    return string_list

def analiza(Lista_1:list[str], Lista_2:list[str]) -> tuple[set[str], set[str], set[str], set[str]]:
    Zakupy = set(Lista_1)
    Zakupy_2 = set(Lista_2)

    wspulne = Zakupy.intersection(Zakupy_2)

    unikalne = Zakupy.difference(Zakupy_2)
    unikalne_2 = Zakupy_2.difference(Zakupy)

    suma = Zakupy.union(Zakupy_2)
    return (wspulne, unikalne, unikalne_2, suma)
    

try:
    Lista_1 = wczytanie()
    Lista_2 = wczytanie()

    wspulne, unikalne, unikalne_2, suma = analiza(Lista_1, Lista_2)
    print("Wspulne produkty: ", wspulne)
    print("unikalne dla pierwszej dsoby: ", unikalne)
    print("unikalne dla drugiej osoby: ", unikalne_2)
    print("Suma: ", suma)
    
except Exception as e:
    print("Wystapil blad: ", e)