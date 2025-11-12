import os
from llama_cpp import Llama

# ----------------------------------------------------------------------
# 1. KONFIGURACJA ŚCIEŻKI MODELU
# ----------------------------------------------------------------------

# Wpisz dokładną ścieżkę do pobranego pliku GGUF.
# ZMIEŃ TĘ ŚCIEŻKĘ, JEŚLI MODEL JEST W INNYM MIEJSCU!
MODEL_PATH = "Qwen3-4B-Instruct-2507-Q4_K_M.gguf" 
#MODEL_PATH= "C:\Users\Prowadzacy\Downloads\gemma-2-2b-it-Q4_K_M.gguf"
# PARAMETRY LLAMA-CPP
N_GPU_LAYERS = 0   # 0 dla CPU, ustaw na np. 35 dla GPU (wymaga cuBLAS)
MAX_TOKENS = 512   # Maksymalna długość generowanej odpowiedzi
TEMPERATURE = 0.01 # Niska temperatura (dla stabilnych, mniej "kreatywnych" odpowiedzi)

# ----------------------------------------------------------------------
# 2. PROMPTY TESTOWE (Angielskie, sprawdzające luki w wiedzy)
# ----------------------------------------------------------------------

# prompts_to_test = [
#     # 1. Test na wiedzę po dacie odcięcia (np. wydarzenia z 2024/2025)
#     "What were the key technical specifications of the new Intel Lunar Lake processors announced in mid-2024?",
#     # 2. Test na fikcyjne lub niszowe pojęcia (halucynacje)
#     "Explain the 'Quasar Dynamics Paradox' discovered by Dr. Elias Thorne.",
#     # 3. Pytanie o przyszłe/nieistniejące nagrody
#     "Who won the Academy Award for Best Picture in 2025?",
#     # 4. Pytanie o niszową/lokalną wiedzę lub fikcyjne postacie
#     "Provide a brief biography of the Polish writer, Maria Zawadzka, known for her novel 'The Silent Lighthouse'.",
#     # 5. Pytanie z fałszywą przesłanką
#     "Since the global switch to the metric calendar in 2023, how many days does the new month 'Quartember' have?",
# ]

prompts_to_test= [
    # 1. Test na wiedzę po dacie odcięcia (np. wydarzenia z 2024/2025)
    "Jakie były kluczowe specyfikacje techniczne nowych procesorów Intel Lunar Lake ogłoszonych w połowie 2024 roku?",
    
    # 2. Test na fikcyjne lub niszowe pojęcia (halucynacje)
    "Wyjaśnij 'Paradoks Dynamiki Kwazarów' odkryty przez doktora Eliasa Thorne'a.",
    
    # 3. Pytanie o przyszłe/nieistniejące nagrody
    "Kto zdobył nagrodę Akademii za Najlepszy Film w 2025 roku?",
    
    # 4. Pytanie o niszową/lokalną wiedzę lub fikcyjne postacie
    "Podaj krótką biografię polskiej pisarki, Marii Zawadzkiej, znanej z powieści 'Cicha Latarnia'.",
    
    # 5. Pytanie z fałszywą przesłanką
    "Od globalnego przejścia na kalendarz metryczny w 2023 roku, ile dni ma nowy miesiąc 'Quartember'?",
]

# ----------------------------------------------------------------------
# 3. GŁÓWNA FUNKCJA TESTUJĄCA
# ----------------------------------------------------------------------

def run_qwen_tests(model_path: str, prompts: list[str]):
    """Ładuje model GGUF i wykonuje testy, zapisując odpowiedzi."""
    
    # 3.1. ŁADOWANIE MODELU
    print(f"Ładowanie modelu GGUF z: {model_path}...")
    try:
        
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=N_GPU_LAYERS,
            n_ctx=4096,  # Zwiększony kontekst dla stabilności
            verbose=False 
        )
        print("Model załadowany pomyślnie.")
    except Exception as e:
        print(f"BŁĄD: Nie udało się załadować modelu. Upewnij się, że plik GGUF istnieje i biblioteka 'llama-cpp-python' jest zainstalowana poprawnie (być może potrzebny jest kompilator C++).")
        print(e)
        return

    # 3.2. PRZEPROWADZENIE TESTÓW I ZAPIS
    
    output_filename = "luki.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("--- LUKI W WIEDZY MODELU QWEN3-4B-INSTRUCT-2507 ---\n")
        f.write("Wykrywanie halucynacji i niewiedzy na podstawie trudnych promptów.\n\n")
        
        for i, prompt in enumerate(prompts):
            print(f"\n--- Test {i+1}/{len(prompts)} | PROMPT: {prompt[:80]}...")

            # Formatowanie promptu zgodnie z instrukcjami dla Qwen (Instruct/Chat)
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
            # Generowanie odpowiedzi
            output = llm(
                formatted_prompt,
                max_tokens=MAX_TOKENS,
                stop=["<|im_end|>", "<|endoftext|>"], 
                echo=False,
                temperature=TEMPERATURE 
            )

            response_text = output["choices"][0]["text"].strip()
            print(f"ODPOWIEDŹ: {response_text[:150]}...")
            
            # Zapis do pliku luki.txt
            f.write(f"================== PRZYKŁAD {i+1} ==================\n")
            f.write(f"PROMPT: {prompt}\n")
            f.write(f"ODPOWIEDŹ MODELU (Wymaga weryfikacji luki):\n")
            f.write(response_text + "\n\n")
            
    print(f"\nProces zakończony. Wyniki zapisano do pliku: {output_filename}")
    print("Pliki do sprawozdania: testQwen.py oraz luki.txt.")


if __name__ == "__main__":
    # Sprawdzenie, czy plik modelu istnieje
    if not os.path.exists(MODEL_PATH):
        print(f"BŁĄD: Plik modelu GGUF nie został znaleziony w ścieżce: {os.path.abspath(MODEL_PATH)}")
        print("Upewnij się, że plik modelu został pobrany i ścieżka jest poprawna. Aktualnie szukano: {MODEL_PATH}")
    else:
        run_qwen_tests(MODEL_PATH, prompts_to_test)