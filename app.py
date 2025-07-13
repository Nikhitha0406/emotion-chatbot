# ✅ app.py — Emotion Chatbot with Email Login + Lazy Loading for Render
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from translator import translate_to_english, detect_language, translate
import os

# Fallback if emotion detector module is missing
try:
    from emotion_detector import detect_emotion
except ImportError:
    def detect_emotion(text):
        return [("neutral", 1.0)]

# Lazy import of AI generator function (to reduce memory on load)
def get_response_generator():
    global generate_response
    if "generate_response" not in globals():
        from ai_generator import generate_response
    return generate_response

# Flask setup
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)
os.makedirs("chat_logs", exist_ok=True)

# DB Models
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    user_msg = db.Column(db.Text)
    bot_reply = db.Column(db.Text)
    emotion = db.Column(db.String(50))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# ----------------- Auth Routes -----------------
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["username"] = email.split("@")[0].capitalize()
            session["history"] = []
            logs = ChatLog.query.filter_by(username=email).all()
            for log in logs:
                session["history"].append({
                    "user": log.user_msg,
                    "bot": log.bot_reply,
                    "emotion": log.emotion
                })
            return redirect(url_for("chat_page"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first():
            flash("Account already exists.", "warning")
            return redirect(url_for("signup"))
        hashed = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = email.split("@")[0].capitalize()
        session["history"] = []
        return redirect(url_for("chat_page"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ----------------- Chat Page -----------------
@app.route("/chat_page")
def chat_page():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session['username'], history=session['history'])

# ----------------- Chat API -----------------
@app.route("/chat", methods=["POST"])
def chat():
    if "username" not in session:
        return jsonify({"response": "🔐 Please log in first."})

    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "❗ Please enter a message."})

    # 🌍 Detect language
    original_lang = detect_language(user_input)

    # 🌐 Translate to English
    translated_input = translate_to_english(user_input)

    # 🔍 Detect emotion
    emotion_scores = detect_emotion(translated_input)
    primary_emotion, _ = emotion_scores[0] if emotion_scores else ("neutral", 1.0)

    # 💬 Lazy load response generator
    generate_response = get_response_generator()

    # 💬 Generate response in English
    english_response = generate_response(primary_emotion, translated_input)

    # 🌐 Translate back to original language
    final_response = translate(english_response, target=original_lang) if original_lang != "en" else english_response

    # 🧠 Save history
    session["history"].append({
        "user": user_input,
        "bot": final_response,
        "emotion": primary_emotion
    })
    session.modified = True

    new_chat = ChatLog(
        username=session['username'],
        user_msg=user_input,
        bot_reply=final_response,
        emotion=primary_emotion
    )
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({
        "emotions": emotion_scores,
        "response": final_response
    })

# ----------------- Main -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
