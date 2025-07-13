try:
    from transformers import pipeline
    emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)

    def detect_emotion(text):
        results = emotion_pipeline(text)[0]
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        return [(e["label"], round(e["score"], 4)) for e in sorted_results[:2]]

except Exception as e:
    print(f"Emotion detection model error: {e}")
    def detect_emotion(text):
        return [("neutral", 1.0)]
