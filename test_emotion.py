from emotion_detector import detect_emotion

text = input("Enter a message: ")
emotion = detect_emotion(text)
print(f"Detected emotion: {emotion}")
