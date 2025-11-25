import time
import datetime
from fastmcp import FastMCP

# Upewnij się, że masz zainstalowaną bibliotekę fastmcp:
# pip install fastmcp

# 1. INICJALIZACJA SERWERA MCP
# Musimy zainicjalizować instancję FastMCP PRZED funkcjami,
# aby dekorator @mcp.tool mógł działać.
# Narzędzia zostaną automatycznie zarejestrowane po użyciu dekoratora.
mcp = FastMCP(name="Server MCP")

# 2. Narzędzie bezparametryczne: Pobiera losowy, inspirujący cytat.
@mcp.tool
def pobierz_cytat_dnia() -> str:
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
    index = int(time.time() * 1000) % len(cytaty)
    return cytaty[index]

# 3. Narzędzie parametryczne: Oblicza wiek psa.
@mcp.tool
def oblicz_wiek_psa(lata_czlowieka: int) -> str:
    """
    Oblicza wiek psa w latach psich, przyjmując prosty przelicznik 1:7.

    :param lata_czlowieka: Wiek psa podany w latach ludzkich (int).
    :return: Sformatowany ciąg znaków z wynikiem lub komunikat o błędzie.
    """
    if lata_czlowieka < 0:
        return "Błąd: Wiek psa musi być liczbą nieujemną."

    wiek_psi = lata_czlowieka * 7
    return f"Pies w wieku {lata_czlowieka} lat ma przybliżony wiek {wiek_psi} lat w 'latach psich'."

# 4. Narzędzie bezparametryczne: Pobiera aktualny czas.
@mcp.tool
def pobierz_lokalny_czas() -> str:
    """
    Zwraca aktualny czas lokalny serwera.
    """
    return datetime.datetime.now().strftime("Aktualny czas lokalny serwera: %Y-%m-%d %H:%M:%S")

def main():

    print(f"Serwer MCP ({mcp.name}) uruchomiony w trybie STDIO. Aby zakończyć, użyj Ctrl+C.")
    print("Oczekuje na dane wejściowe w formacie JSON (FastMCP Tool Call)...")

    # 5. Uruchomienie trybu STDIO na globalnej instancji mcp
    # Używamy mcp.run() zgodnie z Twoim działającym wzorcem
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nSerwer STDIO zakończył działanie (Ctrl+C).")
    except Exception as e:
        print(f"\nBłąd podczas działania serwera STDIO: {e}")


if __name__ == "__main__":
    main()