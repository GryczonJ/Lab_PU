# Zadanie 3: Praca z zbiorami
# Stwórz program, który:
#  pobiera dwie listy zakupów od dwóch osób,
#  konwertuje je na zbiory,
#  wyświetla:
#     o wspólne produkty (część wspólna),
#     o produkty unikalne dla każdej osoby (różnica),
#     o pełną listę produktów (suma zbiorów).

# from typeguard import typechecked

# @typechecked

# df = pd.DataFrame(data)
# print(df)

def wczytanie():
    zakupy = input("Podaj produktow: ")
    srting_list = zakupy.split(',')

    int_lista = list(map(int, srting_list))
    return int_lista

def analiza(Lista_1, Lista_2):
    Zakupy = set(Lista_1)
    Zakupy_2 = set(Lista_2)
    
    wspulne = Zakupy.intersection(Zakupy_2)

    unikalne = Zakupy.difference(Zakupy_2)
    unikalne_2 = Zakupy_2.difference(Zakupy)

    suma = Zakupy.union(Zakupy_2)
    print("Wspulne produkty: ", wspulne)
    print("unikalne dla pierwszej dsoby: ", unikalne)
    print("unikalne dla drugiej osoby: ", unikalne_2)

    print("Suma: ", suma)
