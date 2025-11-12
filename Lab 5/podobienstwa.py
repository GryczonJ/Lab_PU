# import google.generativeai as genai

# # Konfiguracja klucza API
# genai.configure(api_key="AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs")
# # Przykładowy tekst
# text = "To jest przykładowy tekst, dla którego pobieramy embedding."
# # Pobranie embeddingu
# embedding = genai.embed_content(

#     model="models/text-embedding-004",  # aktualny model embeddingowy Gemini

#     content=text,

# )
# # Wynik to słownik z m.in. kluczem 'embedding'
# print(embedding['embedding'])
# print(f"Długość wektora: {len(embedding['embedding'])}")

import numpy as np
import google.generativeai as genai
# Nie importujemy os ani google.generativeai.errors, by uniknąć błędu
# Konfiguracja klucza API
# UWAGA: Ten klucz jest publiczny, usuń go i użyj zmiennej środowiskowej
genai.configure(api_key="AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs")

# UŻYTY MODEL EMBEDDINGOWY
MODEL_NAME = "models/text-embedding-004" 

# --- DANE ZADANIA ---
#https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/blob/main/Qwen3-4B-Instruct-2507-Q4_K_M.gguf

# 3 Pytania
questions = [
    "Jakie są główne zalety nauki programowania w Pythonie?",
    "Wytłumacz koncepcję czarnych dziur w astrofizyce.",
    "Jaki jest wpływ sztucznej inteligencji na rynek pracy?"
]

# 7 Tekstów różnej treści
texts = [
    "Python jest ceniony za prostotę składni i dużą społeczność, co ułatwia naukę i debugowanie. Jest wszechstronny, używany od web developmentu po analizę danych.", # Q1 powiązany
    "Znajomość Pythona otwiera drzwi do kariery w data science i machine learningu, co jest kluczowe w nowoczesnej gospodarce.", # Q1 powiązany
    "Czarne dziury to obszary czasoprzestrzeni o tak silnym polu grawitacyjnym, że nic, nawet światło, nie może z nich uciec. Powstają w wyniku kolapsu masywnych gwiazd.", # Q2 powiązany
    "Horyzont zdarzeń to granica wokół czarnej dziury, po przekroczeniu której powrót jest niemożliwy. W centrum znajduje się osobliwość. Einsteina równania pola.", # Q2 powiązany
    "Wpływ AI jest dwojaki: z jednej strony automatyzuje rutynowe zadania, co może prowadzić do redukcji miejsc pracy w niektórych sektorach, np. w obsłudze klienta.", # Q3 powiązany
    "Z drugiej strony, AI tworzy nowe stanowiska pracy, wymagające umiejętności w jej projektowaniu, utrzymaniu i nadzorowaniu, np. inżynierowie promptów i analitycy danych.", # Q3 powiązany
    "Podstawowe operacje na listach w Pythonie: dodawanie, usuwanie i sortowanie elementów." # Tekst powiązany z Pythonem, mniej informacyjny niż T1 i T2
]


# --- FUNKCJE POMOCNICZE (OBLICZENIA) ---

def get_embeddings(texts_list: list[str], task_type: str) -> np.ndarray:
    """Uzyskuje embeddingi dla listy tekstów."""
    response = genai.embed_content(
        model=MODEL_NAME,
        content=texts_list,
        task_type=task_type
    )
    return np.array(response['embedding'])

def cosine_similarity(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Oblicza podobieństwo kosinusowe (od 0 do 1)."""
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
    return np.dot(A_norm, B_norm.T)

def euclidean_distance(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Oblicza odległość euklidesową (im mniejsza, tym bliżej)."""
    A_sum_sq = np.sum(A**2, axis=1, keepdims=True)
    B_sum_sq = np.sum(B**2, axis=1)
    distances_sq = A_sum_sq + B_sum_sq - 2 * np.dot(A, B.T)
    distances_sq[distances_sq < 0] = 0
    return np.sqrt(distances_sq)

def dot_product(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Oblicza iloczyn skalarny (podobieństwo, im większe, tym lepiej)."""
    return np.dot(A, B.T)

def format_matrix(matrix: np.ndarray, metric_name: str, questions: list[str], texts: list[str]) -> str:
    """Formatuje macierz i dodaje najbliższy tekst w nawiasach kwadratowych."""
    output = f"--- Macierz Podobieństwa: {metric_name} ---\n\n"
    
    # Nagłówek kolumn
    output += f"{'Pytanie':<10}"
    for i, _ in enumerate(texts):
        output += f"| T{i+1:<8}"
    
    output += f"| Najbliższy Tekst \n"
    output += "-" * (10 + (len(texts) * 10) + 20) + "\n"
    
    # Wiersze (Pytania)
    for i, _ in enumerate(questions):
        row_data = matrix[i, :]
        
        # Wybór najlepszego wyniku (max dla podobieństwa, min dla odległości)
        if metric_name in ["COSINUSOWA", "ILOCZYN SKALARNY"]:
            best_value = np.max(row_data)
            best_index = np.argmax(row_data)
        else: # EUKLIDESOWA
            best_value = np.min(row_data)
            best_index = np.argmin(row_data)
        
        # Wiersz z danymi i formatowaniem
        output += f"Q{i+1:<9}"
        for value in row_data:
            output += f"| {value:8.4f}"
        
        # Wymagany format nawiasów kwadratowych: [T# (tekst), Wartość]
        # Dla spójności użyję [Najbliższy Tekst: T#, Wartość: X.XXX]
        output += f"| [Najbliższy: T{best_index+1}, Wartość: {best_value:.4f}]\n"
        
    output += "\n"
    return output

def check_agreement(cos_matrix: np.ndarray, euc_matrix: np.ndarray, dot_matrix: np.ndarray) -> str:
    """Sprawdza zgodność w wyborze najbliższych tekstów przez różne miary."""
    output = "--- Weryfikacja Zgodności Wyboru Najbliższych Tekstów ---\n\n"
    
    # Znajdowanie indeksów najbliższych tekstów
    cos_closest = np.argmax(cos_matrix, axis=1)
    dot_closest = np.argmax(dot_matrix, axis=1)
    euc_closest = np.argmin(euc_matrix, axis=1)
    
    output += "Indeksy najbliższych tekstów dla każdego pytania:\n"
    output += f"{'Pytanie':<10} | {'Kosinusowa':<12} | {'Euklidesowa':<12} | {'Iloczyn Skalarny':<18} | ZGODNOŚĆ\n"
    output += "-" * 75 + "\n"
    
    is_fully_consistent = True
    
    for i in range(len(cos_closest)):
        cos_idx = cos_closest[i] + 1
        euc_idx = euc_closest[i] + 1
        dot_idx = dot_closest[i] + 1
        
        is_consistent = (cos_idx == euc_idx == dot_idx)
        if not is_consistent:
            is_fully_consistent = False
            
        output += f"Q{i+1:<9} | T{cos_idx:<11} | T{euc_idx:<11} | T{dot_idx:<17} | {'ZGODNE' if is_consistent else 'NIEZGODNE'}\n"

    output += "\n"
    output += f"Wniosek: Zgodność w wyborze najbliższych tekstów: {'TAK' if is_fully_consistent else 'NIE'}\n"
    
    return output


def main():
    
    # --- CZĘŚĆ 1: TEST KOMUNIKACJI (Twój fragment) ---
    test_text = "To jest przykładowy tekst, dla którego pobieramy embedding."
    
    # Pobranie embeddingu
    test_embedding_response = genai.embed_content(
        model=MODEL_NAME, 
        content=test_text,
        task_type="RETRIEVAL_DOCUMENT" 
    )
    test_embedding = test_embedding_response['embedding']
    
    # Przygotowanie wyjścia dla testu
    test_output = f"--- Test Komunikacji z Gemini API ---\n"
    test_output += f"Przykładowy tekst: '{test_text}'\n"
    test_output += f"Wymiar embeddingu: {len(test_embedding)}\n"
    test_output += f"Pierwsze 5 wartości embeddingu: {test_embedding[:5]}\n\n"
    
    print(f"Test komunikacji OK. Długość wektora: {len(test_embedding)}")

    # --- CZĘŚĆ 2: WŁAŚCIWE OBLICZENIA ---
    
    print("Obliczam embeddingi dla pytań i tekstów...")
    Q_embeddings = get_embeddings(questions, "RETRIEVAL_QUERY")
    T_embeddings = get_embeddings(texts, "RETRIEVAL_DOCUMENT")
    
    if Q_embeddings.size == 0 or T_embeddings.size == 0:
        print("Błąd: Nie udało się uzyskać wszystkich embeddingów.")
        return

    # Obliczenie Macierzy Podobieństwa
    cos_sim_matrix = cosine_similarity(Q_embeddings, T_embeddings)
    euc_dist_matrix = euclidean_distance(Q_embeddings, T_embeddings)
    dot_prod_matrix = dot_product(Q_embeddings, T_embeddings)
    
    # Formatowanie wyników
    cos_output = format_matrix(cos_sim_matrix, "COSINUSOWA", questions, texts)
    euc_output = format_matrix(euc_dist_matrix, "EUKLIDESOWA", questions, texts)
    dot_output = format_matrix(dot_prod_matrix, "ILOCZYN SKALARNY", questions, texts)
    agreement_output = check_agreement(cos_sim_matrix, euc_dist_matrix, dot_prod_matrix)
    
    final_output = test_output + cos_output + euc_output + dot_output + agreement_output
    
    # Zapis do pliku
    output_filename = "podobienstwa.txt"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"\nSukces! Wyniki zapisano do pliku: {output_filename}")
        print("Pliki do sprawozdania: podobienstwa.py oraz podobienstwa.txt")
    except IOError as e:
        print(f"Błąd zapisu do pliku {output_filename}: {e}")

if __name__ == "__main__":
    main()