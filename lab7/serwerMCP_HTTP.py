import time
import datetime
from fastmcp import FastMCP

# 1. INICJALIZACJA SERWERA MCP

server = FastMCP("Server-HTTP", "1.2.0")

# 2. Narzędzie bezparametryczne: Pobiera losowy, inspirujący cytat.
@server.tool() # Używamy dekoratora z nawiasami, zgodnie z Twoim przykładem
def pobierz_cytat_dnia() -> dict: # Zmieniono typ zwracany na dict
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

    # Wybór cytatu na podstawie aktualnego czasu (aby był "losowy" w danym momencie)
    # Używamy tej samej logiki, ale zwracamy wynik jako słownik
    index = int(time.time() * 1000) % len(cytaty)
    return {"cytat": cytaty[index]}

# 3. Narzędzie parametryczne: Oblicza wiek psa.
@server.tool()
def oblicz_wiek_psa(lata_czlowieka: int) -> dict: # Zmieniono typ zwracany na dict
    """
    Oblicza wiek psa w latach psich, przyjmując prosty przelicznik 1:7.

    :param lata_czlowieka: Wiek psa podany w latach ludzkich (int).
    :return: Słownik z wynikiem lub komunikat o błędzie.
    """
    if lata_czlowieka < 0:
        return {"blad": "Wiek psa musi być liczbą nieujemną."}

    wiek_psi = lata_czlowieka * 7
    return {
        "lata_czlowieka": lata_czlowieka,
        "wiek_psi": wiek_psi,
        "komunikat": f"Pies w wieku {lata_czlowieka} lat ma przybliżony wiek {wiek_psi} lat w 'latach psich'."
    }

# 4. Narzędzie bezparametryczne: Pobiera aktualny czas.
@server.tool()
def pobierz_lokalny_czas() -> dict: # Zmieniono typ zwracany na dict
    """
    Zwraca aktualny czas lokalny serwera.
    """
    # Zmieniono format, aby był bardziej zgodny ze wzorcem JSON/dict
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"aktualny_czas_lokalny": now}

# 5. Uruchomienie trybu HTTP
if __name__ == "__main__":
    # Używamy server.run() z transport="http", aby uruchomić serwer jako API HTTP.
    # Domyślnie działa na porcie 8000.
    print(f"Serwer MCP ({server.name}) uruchomiony. Uruchamianie transportu HTTP...")
    print("Dostępny pod adresem: http://127.0.0.1:8000/ ")
    server.run(transport="http")