import random
import datetime
from fastmcp import FastMCP


server = FastMCP("Server-HTTP", "1.0.0")


# Narzędzie bezparametryczne — losowy cytat
@server.tool()
def losowy_cytat() -> dict:
    cytaty = [
        "Rób to, co kochasz.",
        "Małe zwycięstwa składają się na sukces.",
        "Myśl jasno, działaj odważnie.",
        "Porażka to krok ku doskonałości.",
        "Ciekawość otwiera drzwi."
        ]
    return {"quote": random.choice(cytaty)}


# Narzędzie parametryczne — analiza tekstu
@server.tool()
def analizuj_tekst(params: dict) -> dict:
    text = params.get("text", "") if isinstance(params, dict) else ""
    words = [w for w in text.split() if w.strip()]
    word_count = len(words)
    char_count = len(text)
    freq = {}
    for w in words:
        k = w.strip().lower()
        freq[k] = freq.get(k, 0) + 1
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        top_words = [{"word": w, "count": c} for w, c in top]
    return {
        "word_count": word_count,
        "char_count": char_count,
        "top_words": top_words
    }


if __name__ == "__main__":
    # Uruchomienie HTTP + SSE. Domyślny port 8000
    server.run(transport="http", host="127.0.0.1", port=8000)