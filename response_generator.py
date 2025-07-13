import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_response(emotion, user_input):
    prompt = f"""
You are a friendly, empathetic chatbot. The user is feeling {emotion}.
Respond with emotional support and suggestions (music, quotes, self-care), and always ask: "How are you feeling now?"

User: {user_input}
Bot:"""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",  # your app URL or GitHub repo
            "X-Title": "Emotion Support Chatbot"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a compassionate emotional support assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        response = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"⚠️ Error: {str(e)}"
