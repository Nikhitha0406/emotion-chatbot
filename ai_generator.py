import httpx
import os
import re
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def format_bot_response(text):
    # Add newlines before numbered lists or bullet points
    text = re.sub(r'(\d+\.)', r'\n\1', text)
    text = re.sub(r'(?<=:)\s*', '\n', text)  # Add newline after colon
    text = re.sub(r'\n{2,}', '\n\n', text)   # Ensure only max 2 line breaks
    text = text.replace("How are you feeling now?", "\n\n🧠 *How are you feeling now?*")
    return text.strip()

def generate_response(emotion, user_input):
    emotion = emotion or "neutral"

    if emotion.lower() in ["joy", "sadness", "anger", "fear", "disgust"]:
        prompt = f"""
The user is feeling {emotion}.
Respond with emotional support, give comfort suggestions (music, quotes, self-care),
and end with a follow-up like "How are you feeling now?".
User: {user_input}
Bot:"""
    else:
        prompt = f"""
Answer the user's question clearly and helpfully.
Avoid unnecessary emotional suggestions unless the message expresses feelings.
User: {user_input}
Bot:"""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Emotion Support Chatbot"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful and emotionally intelligent chatbot."},
                {"role": "user", "content": prompt}
            ]
        }

        response = httpx.post("https://openrouter.ai/api/v1/chat/completions",
                              headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        raw_text = response.json()["choices"][0]["message"]["content"].strip()
        formatted_text = format_bot_response(raw_text)  # ✅ Format it here
        return formatted_text

    except Exception as e:
        return f"⚠️ Error: {str(e)}"
