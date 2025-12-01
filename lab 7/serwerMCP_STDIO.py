import time
import datetime
from fastmcp import FastMCP
import random # Dodajemy random, ponieważ go użyjemy, chociaż w oryginalnym kodzie nie był wprost użyty do wyboru cytatu

# 1. INICJALIZACJA SERWERA MCP
# Używamy nazwy 'server' i dodajemy wersję, zgodnie ze wzorem.
# FastMCP(name, version)
server = FastMCP("Server-Przeliczenia", "1.2.0")

# 2. Narzędzie bezparametryczne: Pobiera losowy, inspirujący cytat.
# Zmieniamy typ zwracany na dict.
@server.tool()
def pobierz_cytat_dnia() -> dict:
    """
    Zwraca losowy, inspirujący cytat dnia.
    """
    # Lista cytatów
    cytaty = [
    "Jedyne, co stoi pomiędzy Tobą a Twoim celem, to historyjka, którą sobie opowiadasz.",
    "Przyszłość należy do tych, którzy wierzą w piękno swoich marzeń.",
    "Rób, co możesz, z tym, co masz, tam, gdzie jesteś.",
    "Najlepszym sposobem przewidzenia przyszłości jest jej stworzenie."
    ]

    # Używamy random.choice dla prostszej losowości, ale możemy też zostawić oryginalną logikę.
    # Wracamy do użycia `random.choice`, ponieważ jest to bardziej czytelne.
    cytat = random.choice(cytaty)
    
    # Zwracamy słownik, zgodnie ze wzorem.
    return {"cytat": cytat}

# 3. Narzędzie parametryczne: Oblicza wiek psa.
# Zmieniamy typ zwracany na dict.
@server.tool()
def oblicz_wiek_psa_uniwersalna(arg):
    # Sprawdzenie, czy to jest słownik (dict)
    if isinstance(arg, dict):
        if "lata_czlowieka" in arg:
            lata_czlowieka = arg["lata_czlowieka"]
        else:
            return {"blad": "Słownik nie zawiera klucza 'lata_czlowieka'."}
    
    # Sprawdzenie, czy to jest sama liczba (int/float)
    elif isinstance(arg, (int, float)):
        lata_czlowieka = arg
        
    else:
        return {"blad": "Nieobsługiwany typ danych wejściowych."}
    
    # Dalsza logika obliczeń...
    wiek_psi = lata_czlowieka * 7
    return {"wiek": wiek_psi, "opis": f"Pies w wieku {lata_czlowieka} lat ma przybliżony wiek {wiek_psi} lat w 'latach psich'."}

# def oblicz_wiek_psa(lata_czlowieka: int) -> dict:
#     """
#     Oblicza wiek psa w latach psich, przyjmując prosty przelicznik 1:7.

#     :param lata_czlowieka: Wiek psa podany w latach ludzkich (int).
#     :return: Sformatowany ciąg znaków z wynikiem lub komunikat o błędzie, opakowany w słownik.
#     """
#     if lata_czlowieka < 0:
#         # Zwracamy słownik z informacją o błędzie.
#         return {"blad": "Wiek psa musi być liczbą nieujemną."}

#     wiek_psi = lata_czlowieka * 7
#     # Zwracamy słownik z wynikiem.
#     return {"wiek": wiek_psi, "opis": f"Pies w wieku {lata_czlowieka} lat ma przybliżony wiek {wiek_psi} lat w 'latach psich'."}

# 4. Narzędzie bezparametryczne: Pobiera aktualny czas.
# Zmieniamy typ zwracany na dict.
@server.tool()
def pobierz_lokalny_czas() -> dict:
    """
    Zwraca aktualny czas lokalny serwera.
    """
    czas = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Zwracamy słownik, zgodnie ze wzorem.
    return {"aktualny_czas": czas}

if __name__ == "__main__":
    # Uruchomienie serwera w trybie HTTP, zgodnie ze wzorem.
    server.run(transport="http")