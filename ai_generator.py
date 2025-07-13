# ai_generator.py — OpenRouter API Response Generator
import os
import httpx
from dotenv import load_dotenv

load_dotenv()  # ensure .env is loaded

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ✅ Debug Print (remove this after testing)
print("🔑 Loaded API Key:", OPENROUTER_API_KEY)

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://emotion-chatbot-6.onrender.com",  # replace with your actual site if needed
    "X-Title": "Emotion Chatbot"
}

def generate_response(emotion, prompt):
    try:
        system_prompt = f"You are an empathetic assistant. The user feels {emotion}."
        data = {
            "model": "mistralai/mistral-7b-instruct",  # or another OpenRouter-supported model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }

        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )

        if response.status_code == 401:
            print("❌ Unauthorized: Check API key or headers.")
            return "⚠️ I'm having trouble connecting to the language model. Please try again later."

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ Error generating AI response:", str(e))
        return "⚠️ Something went wrong. Please try again later."
