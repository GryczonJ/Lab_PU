# Korzystając z darmowej usługi REST API https://gutendex.com/ pobierz 32 książki (1
# strona). Wyświetl na konsoli tytuły i streszczenia. 

import requests

# URL domyślnie zwracający 32 książki
API_URL = "https://gutendex.com/books/"

# Wykonanie zapytania i parsowanie odpowiedzi JSON
try:
    data = requests.get(API_URL).json()
except Exception as e:
    print(f"Błąd pobierania danych: {e}")
    exit()

# Iteracja po 32 książkach
for book in data.get('results', []):
    title = book.get('title', 'Brak tytułu')
    
    # API Gutendex nie udostępnia streszczeń.
    summary = book.get('summaries') or "Brak streszczenia dostępnego."
    
    # Minimalne wyświetlenie na konsoli
    print(f"TYTUŁ: {title}")
    print(f"STRESZCZENIE: {summary}\n")
     