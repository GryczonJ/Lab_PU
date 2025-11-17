import datetime
import requests
import os
import json

from google import genai
from google.genai import types

API_KEY = "AIzaSyDol30cA_ECLlc3bc6vmu1XSV1ixkJ23xs" 

import LLM_FC as llm_fc

# ----------------------------------------------------

def ZnajdzStrony(haslo: str):
    """Wyszukuje strony w DuckDuckGo API."""
    url = "https://api.duckduckgo.com/"
    params = {
        "q": haslo,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    wyniki = []

    # DuckDuckGo korzysta z list 'RelatedTopics'
    for item in data.get("RelatedTopics", []):
        if "FirstURL" in item and "Text" in item:
            wyniki.append({
                "url": item["FirstURL"],
                "opis": item["Text"]
            })
        # czasem wchodzą podlisty
        if "Topics" in item:
            for t in item["Topics"]:
                if "FirstURL" in t and "Text" in t:
                    wyniki.append({
                        "url": t["FirstURL"],
                        "opis": t["Text"]
                    })

    return wyniki


def PobierzStrone(url: str):
    """Pobiera HTML strony pod wskazanym URL."""
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return {"html": r.text}


# Lista dostępnych funkcji dla Function Calling
AVAILABLE_TOOLS = {
    "ZnajdzStrony": ZnajdzStrony,
    "PobierzStrone": PobierzStrone,
}

# Definicje narzędzi w formacie zrozumiałym dla API Gemini
TOOL_SCHEMAS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="ZnajdzStrony",
            description="Wyszukuje strony pasujące do hasła, używając darmowego API DuckDuckGo. Zwraca listę obiektów z polami url i opis.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "haslo": types.Schema(type=types.Type.STRING)
                },
                required=["haslo"]
            ),
        ),
        types.FunctionDeclaration(
            name="PobierzStrone",
            description="Pobiera HTML wskazanej strony internetowej.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "url": types.Schema(type=types.Type.STRING)
                },
                required=["url"]
            ),
        )
    ])
]

if __name__ == "__main__":
    llm_fc.PrzeprowadzTestyGemini(use_function_calling=True, tool_schemas=TOOL_SCHEMAS, available_tools=AVAILABLE_TOOLS)