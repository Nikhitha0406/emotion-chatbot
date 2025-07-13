import requests

print("🤖 Emotion Chatbot (type 'exit' to quit)\n")

history = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Thank you for chatting! Take care 😊")
        break

    try:
        response = requests.post("http://127.0.0.1:5000/chat", json={"message": user_input})
        data = response.json()

        emotions = data['emotions']  # list of [label, score]
        bot_reply = data['response']

        # Save history
        history.append({
            "user": user_input,
            "emotions": emotions,
            "bot": bot_reply
        })

        top_emotion_label = emotions[0][0]
        emotion_summary = ", ".join([f"{label} ({score})" for label, score in emotions])

        print(f"Bot ({top_emotion_label}): {bot_reply}")
        print(f"Detected emotions: {emotion_summary}\n")

    except Exception as e:
        print("❌ Error: Could not reach chatbot API or parse response.\n")
        print(e)

# Save chat log to file
with open("chat_log.txt", "w", encoding="utf-8") as f:
    for turn in history:
        f.write(f"You: {turn['user']}\n")
        f.write(f"Bot ({turn['emotions'][0][0]}): {turn['bot']}\n")
        f.write(f"Detected: {', '.join([f'{e[0]} ({e[1]})' for e in turn['emotions']])}\n\n")

print("📝 Chat saved to chat_log.txt")
