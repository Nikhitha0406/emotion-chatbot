import requests
import os

# Load Hugging Face API key from environment variable
HF_API_KEY = os.getenv("HF_API_KEY")

def detect_emotion(text):
    API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        response.raise_for_status()
        results = response.json()[0]  # List of emotion scores

        # Sort emotions by score (descending) and return top 2
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        return [(item["label"].lower(), round(item["score"], 4)) for item in sorted_results[:2]]

    except Exception as e:
        print(f"Emotion detection API error: {e}")
        return [("neutral", 1.0)]
