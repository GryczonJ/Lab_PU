import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

STRESZCZENIE_ANGIELSKIE = (
        "In 'The Algorithm' a disillusioned programmer discovers an ancient sorting algorithm "
        "that doesn't just order data, but subtly affects the causality of the real world. "
        "He must choose between restoring cosmic entropy and fulfilling his personal desires."
    )

PROMPT_TŁUMACZENIA = (
        "Przetłumacz poniższe streszczenie na język polski. Podaj wyłącznie czyste tłumaczenie, bez żadnych dodatkowych komentarzy ani wstępu:\n\n"
        f"{STRESZCZENIE_ANGIELSKIE}"
    )


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

response = query({
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": PROMPT_TŁUMACZENIA 
                }
            ]
        }
    ],
    "model": "Qwen/Qwen3-VL-235B-A22B-Instruct:novita"
})


if __name__ == "__main__":
    try:
        print(response["choices"][0]["message"]["content"])
    except (KeyError, IndexError) as e:
        print(f"Błąd podczas pobierania odpowiedzi z modelu: {e}")
        print("Pełna odpowiedź:")
        print(response)

# print(response["choices"][0]["message"])
# print("==============================================")
