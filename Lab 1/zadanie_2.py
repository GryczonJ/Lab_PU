# Zadanie 2: Generator raportu z danych liczbowych
# Stwórz program, który:
#  pobiera od użytkownika listę liczb (np. wyniki pomiarów),
#  oblicza sumę, średnią i liczbę dodatnich wartości,
#  wykorzystuje funkcję z type hints, dokumentację (docstring) i wyrażenie lambda,
#  obsługuje wyjątki (np. błędne dane wejściowe). 

def generator(lista:list[float])->tuple[float, float, float]:
    """
        funkcjia do generowania raportu
    """
    if len(lista) == 0:
         raise Exception("pusta lista")

    suma = sum(lista)
    średnia = suma/len(lista)
    dodanie = lambda a: a>0
    liczby_dodanie = filter(dodanie, lista)
    ilość_dodanich_liczb = len(list(liczby_dodanie))
    
    return (suma, średnia, ilość_dodanich_liczb)


def wczytanie_danych()->list[float]:
    """
    funkcja do wczytywania danych od użytkownika
"""
    user_list = input("Podaj listę liczb: ")
    string_list = user_list.split(',')
    float_lista = list(map(float, string_list))
    return float_lista


# Mian
try:
    print(generator(wczytanie_danych()))
except Exception as e:
    print(f"Wystąpił błąd: {e}")
