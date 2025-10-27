# Proszę pobrać do DateFrame z Wikipedii spis wszystkich haseł z wybranej przez siebie
# kategorii wraz linkami do ich podstron. Wypełnić z wykorzystaniem klasy Tabela_
# (pobieranej z modułu utworzonego w poprzednim zadaniu) swoją bazę danych tymi
# hasłami pobierając je w pętli z Wikipedii. Do bazy proszę wstawiać jedynie oczyszczony
# tekst opisu hasła (np. przez wyrażenie regularne), bez znaczników html i elementów
# Wikipedii.
# Następnie zawartość bazy proszę zserializować do pliku wikipedia.json.
# W sprawozdaniu proszę umieć program wikipedia.py oraz wikipedia.json.

import requests as req
import pandas as pd
from bs4 import BeautifulSoup as bs
import jsonpickle
from baza import Tabela_Technika, Hasło
import re
import time

# https://pl.wikipedia.org/wiki/Kategoria:Akcesoria_do_palenia
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(localdb)\\MSSQLLocalDB;"
    "Database=Wikipedia;"
    "Integrated Security=True;"
)

BASE_URL = 'https://pl.wikipedia.org'
URL = f'{BASE_URL}/wiki/Kategoria:Technika'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def pobierz_liste_hasel(url):
    res = req.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = bs(res.text, 'html.parser')
    items = []
    for a in soup.select('#mw-pages ul li a'):
        items.append({'Hasło': a.text, 'Link': BASE_URL + a['href'], 'Treść': ''})
    return pd.DataFrame(items)

def czysc_tekst(html):
    soup = bs(html, 'html.parser')
    content = soup.find("div", class_="mw-content-ltr mw-parser-output")
    if not content: return ""
    for tag in content(['table', 'sup', 'style', 'script']): tag.decompose()
    text = ' '.join(p.get_text() for p in content.find_all('p', recursive=False))
    text = re.sub(r'\[\d+|\[[a-z]\]', '', text)
    return re.sub(r'\s+', ' ', text).strip()



#main 
df = pobierz_liste_hasel(URL)
print(f"Znaleziono {len(df)} haseł.")
baza = Tabela_Technika(connection_string)
for i, row in df.iterrows():
    print(f"Pobieranie: {row['Hasło']}...")
    try:
        r = req.get(row['Link'], headers=HEADERS, timeout=10)
        r.raise_for_status()
        tresc = czysc_tekst(r.text)
        print(f"treść: {tresc[:60]}...")
        df.at[i, 'Treść'] = tresc
        #, row['Link']
        baza.dodaj_hasło(Hasło(1,row['Hasło'], tresc))
    except Exception as e:
        print(f"Błąd przy {row['Hasło']}: {e}")
    time.sleep(1)
baza.zapisz_do_json("wikipedia.json")
print("Zapisano do wikipedia.json")