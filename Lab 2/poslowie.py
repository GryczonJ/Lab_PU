# Korzystając z modułu Request i bs4.BeautifulSoup odbierz w programie Python ze strony
# Sejmu RP nazwiska i imiona wszystkich aktualnych senatorów RP. Zapisz w osobnych
# kolumnach Pandas DateFrame ich imiona i nazwiska. Następnie korzystając z
# możliwości DataFrame należy policzyć: ile jest senatorów i senatorek, ilu senatorów
# obojga płci w nazwiskach ma typowo polskie znaki (korzystając z odpowiedniego
# wyrażenia regularnego i przeznaczonej do tego własnej funkcji polskie_nazwisko, ilu
# posługuje się wieloczłonowym imieniem, a ilu wieloczłonowym nazwiskiem. Do pliku
# senatorowie.txt proszę zapisać wszystkich posłów oraz na końcu obliczone statystyki.
# Proszę sprawdzić, czy liczba posłów się zgadza i ewentualnie poprawić kod.

# W sprawozdaniu proszę umieścić kod senatorowie.py oraz wynik sentorowie.txt

import requests as req
import pandas as pd
import re
from bs4 import BeautifulSoup as bs



def polskie_nazwisko(nazwisko: str)-> bool:
    wzorzec = r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]'
    if re.search(wzorzec, nazwisko): return True
    else: return False

wyjądkowe_męskie_imiona = [
    "Barnaba",
    "Kuba",
    "Kosma",
    "Bonawentura",
    "Izaaka", 
    "Juda"
    "Jarema"
]

def czy_kobieta(imie: str)->bool:
    """Określa płeć"""
    # pierwsze_imie = imie.split()[0]
    # pierwsze_imie[-1] == "a" 
    if  imie[-1] == "a" and (imie not in wyjądkowe_męskie_imiona):
        return True
    else: return False
  

url = 'https://www.senat.gov.pl/sklad/senatorowie/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    # Opcjonalnie można dodać inne nagłówki, np. Accept-Language
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7'
}

response = req.get(url, headers=headers)
if(response.status_code != 200):
    print("Błąd połączenia:", response.status_code)
    exit(1)

response.encoding = 'utf-8' # polskie znaki
html = response.text
soup = bs(html, 'html.parser')

df = pd.DataFrame(columns=['Imię', 'Nazwisko'])

for kontener in soup.find_all("div",class_="col-lg-4 col-md-4 col-sm-4 col-xs-6"):
    a_tag  = kontener.find("a")
    if a_tag:
        pelne_imie_nazwisko = a_tag.get_text( strip = True )
        imie,nazwisko, = pelne_imie_nazwisko.rsplit(" ", 1) #split(" ", 1)
        #print(f"Imię: {imie}, Nazwisko: {nazwisko}")
        df = pd.concat([df, pd.DataFrame({'Imię': [imie], 'Nazwisko': [nazwisko]})], ignore_index=True) 


# main
polskich_nazwisk = df['Nazwisko'].apply(polskie_nazwisko)
posłanki = df ['Imię'].apply(czy_kobieta)


WieloImię = df['Imię'].str.contains(' ')
warunek_spacja = df['Nazwisko'].str.contains(' ')
warunek_myslnik = df['Nazwisko'].str.contains('-')
kobiety = posłanki.sum()
panowie = df['Imię'].count() - kobiety
# print("nazwiska:", polskich_nazwisk.sum())
# print("kobiety", posłanki.sum())

# print("dwa imiona:", WieloImię.sum())
# print("nazwiska", warunek_spacja.sum(),warunek_myslnik.sum())

with open("sentorowie.txt", "w", encoding="utf-8") as file:
    file.write(df[['Imię', 'Nazwisko']].to_csv(sep=' ', index=False, header=False))
    file.write("\n")

    file.write(f"Polskie znaki w nazwisku: {polskich_nazwisk.sum()}\n")
    file.write(f"Liczba senatorek: {kobiety}\n")
    file.write(f"Liczba senatorów: {panowie}\n")
    file.write(f"wieloczłonowym imieniem: {WieloImię.sum()}\n")
    file.write(f"wieloczłonowym nazwiskiem: {warunek_myslnik.sum()}\n")
#{warunek_spacja.sum()},
print("Dane zapisano do pliku 'senatorowie.txt' i przeanalizowano.")