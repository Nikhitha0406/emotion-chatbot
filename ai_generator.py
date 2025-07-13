# ai_generator.py — Emotion-aware, Lazy, Formatted Response via OpenRouter API

import httpx
import os
import re
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def format_bot_response(text):
    """
    Clean and format the AI's response for better readability.
    - Newlines before numbered/bullet lists
    - Newline after colon for clarity
    - Ensures clean spacing
    """
    text = re.sub(r'(\d+\.)', r'\n\1', text)            # Numbered list formatting
    text = re.sub(r'(?<=:)\s*', '\n', text)             # Newline after colon
    text = re.sub(r'\n{2,}', '\n\n', text)              # Max 2 line breaks
    text = text.replace("How are you feeling now?", "\n\n🧠 *How are you feeling now?*")
    return text.strip()

def generate_response(emotion, user_input):
    """
    Send a request to OpenRouter to generate an intelligent or empathetic response,
    based on the detected emotion and user message.
    """

    # Default fallback
    emotion = emotion or "neutral"

    # Prompt varies by emotional intensity
    if emotion.lower() in ["joy", "sadness", "anger", "fear", "disgust"]:
        prompt = f"""
The user is feeling {emotion}.
Respond with emotional support, comfort suggestions (e.g., music, quotes, or self-care),
and end with a follow-up like "How are you feeling now?".
User: {user_input}
Bot:"""
    else:
        prompt = f"""
Answer the user's question clearly and helpfully.
Only provide emotional advice if the message shows strong feelings.
User: {user_input}
Bot:"""

    try:
        # Construct headers
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",  # ✅ Change for production
            "X-Title": "Emotion Support Chatbot"
        }

        # Prepare OpenRouter chat API payload
        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful and emotionally intelligent chatbot."},
                {"role": "user", "content": prompt.strip()}
            ]
        }

        # Send API request
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        # Extract and format the bot's reply
        raw_text = response.json()["choices"][0]["message"]["content"].strip()
        return format_bot_response(raw_text)

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
