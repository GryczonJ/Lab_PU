# Zadanie 2: Generator raportu z danych liczbowych
# Stwórz program, który:
#  pobiera od użytkownika listę liczb (np. wyniki pomiarów),
#  oblicza sumę, średnią i liczbę dodatnich wartości,
#  wykorzystuje funkcję z type hints, dokumentację (docstring) i wyrażenie lambda,
#  obsługuje wyjątki (np. błędne dane wejściowe). 

def generator(lista:list[int])->int:
    """
        funkcjia do generowania raportu
    """
    if len(lista)==0:
         raise Exception("pusta lista")

    suma = sum(lista)
    średnia = suma/len(lista)

    print(f" suma: {suma} ")
    print(f" średnia: { średnia } ")
    

    dodanie = lambda a: a>0
    liczby_dodanie = filter(dodanie, lista)
   
    ilość_dodanich_liczb = len(list(liczby_dodanie))
    
    print(f"dodanich jest: {ilość_dodanich_liczb}")
    return 1


def wczytanie_danych()->list[int]:
    user_list = input("Podaj listę liczb: ")
    srting_list = user_list.split(',')
    int_lista = list(map(int, srting_list))
    return int_lista


# Mian
generator(wczytanie_danych())