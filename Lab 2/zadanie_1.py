# Korzystając z modułu Request i bs4.BeautifulSoup odbierz w programie Python ze strony
# Sejmu RP nazwiska i imiona wszystkich aktualnych posłów na sejm. Zapisz w osobnych
# kolumnach Pandas DateFrame ich imiona i nazwiska. Następnie korzystając z
# możliwości DataFrame należy policzyć:,ile jest posłów i posłanek, ilu posłów obojga płci
# w nazwiskach ma typowo polskie znaki (korzystając z odpowiedniego wyrażenia
# regularnego i przeznaczonej do tego własnej funkcji polskie_nazwisko, ilu posługuje się
# wieloczłonowym imieniem, a ilu wieloczłonowym nazwiskiem. Do pliku poslowie.txt
# proszę zapisać wszystkich posłów oraz na końcu obliczone statystyki. Proszę sprawdzić,
# czy liczba posłów się zgadza i ewentualnie poprawić kod.
# W sprawozdaniu proszę umieścić kod poslowie.py oraz wynik poslowie.txt

import request as req
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.sejm.gov.plklad/sen
