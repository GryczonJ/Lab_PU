# Zadanie 2: Generator raportu z danych liczbowych 
# Stwórz program, który: 
#  pobiera od użytkownika listę liczb (np. wyniki pomiarów), 
#  oblicza sumę, średnią i liczbę dodatnich wartości, 
#  wykorzystuje funkcję z type hints, dokumentację (docstring) i wyrażenie lambda, 
#  obsługuje wyjątki (np. błędne dane wejściowe)

def generate_report(data: list[float]) -> dict[str, float]:
    """
    Generuje raport z danych liczbowych.

    Args:
        data (list[float]): Lista danych liczbowych.

    Returns:
        dict[str, float]: Słownik z wynikami analizy.
    """
    if not data:
        raise ValueError("Lista danych jest pusta.")

    # Obliczenia
    total = sum(data)
    average = total / len(data)
    positive_count = len(list(filter(lambda x: x > 0, data)))

    # Generowanie raportu
    report = {
        "suma": total,
        "średnia": average,
        "liczba_dodatnich": positive_count
    }

    return report
# Pobieranie danych od użytkownika
user_input = input("Podaj listę liczb oddzielonych spacjami: ")
try:
    data = [float(x) for x in user_input.split()]
    report = generate_report(data)
    print("Raport z danych:")
    print(f"Suma: {report['suma']}")
    print(f"Średnia: {report['średnia']}")
    print(f"Liczba dodatnich wartości: {report['liczba_dodatnich']}")
except ValueError as e:
    print(f"Błąd danych wejściowych: {e}")

