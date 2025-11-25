import time
import datetime
from fastmcp import FastMCP
import uvicorn # uvicorn jest wymagany do uruchomienia serwera FastMCP w trybie HTTP

# Upewnij się, że masz zainstalowane wymagane biblioteki:
# pip install fastmcp uvicorn

# --- KONFIGURACJA SERWERA ---
HOST = "127.0.0.1" # Dostępny lokalnie
PORT = 8000
# -----------------------------

# 1. INICJALIZACJA SERWERA MCP
# FastMCP w trybie HTTP tworzy wewnętrznie aplikację FastAPI
#mcp = FastMCP(name="Server MCP HTTP", http_url=f"http://{HOST}:{PORT}")
mcp = FastMCP(name="Server MCP HTTP")
# URL zostanie automatycznie ustawiony jako host:port, gdy uruchomisz serve_http

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

# 4. Narzędzie bezparametryczne: Pobiera aktualny czas (przeniesione z oryginalnego kodu, ale w pełni funkcjonalne).
@mcp.tool
def pobierz_lokalny_czas() -> str:
    """
    Zwraca aktualny czas lokalny serwera.
    """
    return datetime.datetime.now().strftime("Aktualny czas lokalny serwera: %Y-%m-%d %H:%M:%S")


def main():
    print(f"Serwer MCP ({mcp.name}) uruchamia się w trybie HTTP SSE...")
    print(f"Adres serwera: http://{HOST}:{PORT}")
    print("Aby zakończyć, użyj Ctrl+C.")
    
    try:
        # Krok 1: Usunięcie argumentu http_url z inicjalizacji FastMCP (jeśli nie zaktualizowałeś)
        # Krok 2: Użycie samego obiektu 'mcp' zamiast 'mcp.app' jako aplikacji ASGI 
        uvicorn.run(
            mcp, # Zmiana tutaj! Uruchamiamy obiekt mcp, zakładając, że implementuje protokół ASGI
            host=HOST, 
            port=PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nSerwer HTTP zakończył działanie (Ctrl+C).")
    except Exception as e:
        print(f"\nBłąd podczas działania serwera HTTP: {e}")

if __name__ == "__main__":
    main()