# translator.py
import httpx

def detect_language(text):
    try:
        res = httpx.post(
            "https://libretranslate.de/detect",
            json={"q": text},
            timeout=10
        )
        res.raise_for_status()
        lang_data = res.json()
        return lang_data[0]['language'] if lang_data else "en"
    except Exception as e:
        print(f"[Language Detection Error] {e}")
        return "en"

def translate_to_english(text):
    return translate(text, target="en")

def translate(text, target, source="auto"):
    try:
        res = httpx.post(
            "https://libretranslate.de/translate",
            json={"q": text, "source": source, "target": target, "format": "text"},
            timeout=10
        )
        res.raise_for_status()
        return res.json()["translatedText"]
    except Exception as e:
        print(f"[Translation Error] {e}")
        return text
