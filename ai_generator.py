import httpx
import os
import re
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def format_bot_response(text):
    text = re.sub(r'(\d+\.)', r'\n\1', text)
    text = re.sub(r'(?<=:)\s*', '\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = text.replace("How are you feeling now?", "\n\n🧠 *How are you feeling now?*")
    return text.strip()

def generate_response(emotion, user_input):
    emotion = emotion or "neutral"

    if emotion.lower() in ["joy", "sadness", "anger", "fear", "disgust"]:
        prompt = f"""
The user is feeling {emotion}.
Respond with emotional support, comfort suggestions (music, quotes, self-care),
and end with "How are you feeling now?".
User: {user_input}
Bot:"""
    else:
        prompt = f"""
Answer the user's question clearly and helpfully.
Avoid emotional suggestions unless the user expresses emotions.
User: {user_input}
Bot:"""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://emotion-chatbot-3.onrender.com",  # ✅ must be your Render URL
            "X-Title": "Emotion Support Chatbot"
        }

        payload = {
            "model": "mistral:instruct",  # ✅ OpenRouter uses alias format
            "messages": [
                {"role": "system", "content": "You are a helpful and emotionally intelligent chatbot."},
                {"role": "user", "content": prompt}
            ]
        }

        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )

        response.raise_for_status()
        raw_text = response.json()["choices"][0]["message"]["content"]
        return format_bot_response(raw_text)

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
