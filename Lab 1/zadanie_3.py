# Zadanie 3: Praca z zbiorami
# Stwórz program, który:
#  pobiera dwie listy zakupów od dwóch osób,
#  konwertuje je na zbiory,
#  wyświetla:
#     o wspólne produkty (część wspólna),
#     o produkty unikalne dla każdej osoby (różnica),
#     o pełną listę produktów (suma zbiorów).

import pandas as pd
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
    df = pd.DataFrame(Lista_1)