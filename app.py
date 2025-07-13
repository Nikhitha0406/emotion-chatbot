# ✅ app.py — Emotion Chatbot with Email Login Only (OpenRouter-Ready)
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from ai_generator import generate_response
from translator import translate_to_english, detect_language, translate
  # ✅ Only one import
import os

# Fallbacks if emotion detection modules are missing
try:
    from emotion_detector import detect_emotion
except ImportError:
    def detect_emotion(text):
        return [("neutral", 1.0)]

# Flask Setup
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Ensure chat log directory exists
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

# --------------------------
# Login and Signup Routes
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

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Account already exists.", "warning")
            return redirect(url_for("signup"))

        # Create new user
        hashed = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()

        # ✅ Auto-login after signup
        session["username"] = email.split("@")[0].capitalize()
        session["history"] = []
        return redirect(url_for("chat_page"))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# --------------------------
@app.route("/chat_page")
def chat_page():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session['username'], history=session['history'])
@app.route("/chat", methods=["POST"])
def chat():
    if "username" not in session:
        return jsonify({"response": "🔐 Please log in first."})

    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "❗ Please enter a message."})

    # 🌍 Detect original language
    original_lang = detect_language(user_input)

    # 🌐 Translate input to English
    translated_input = translate_to_english(user_input)

    # 🔍 Detect emotion
    emotion_scores = detect_emotion(translated_input)
    primary_emotion, score = emotion_scores[0] if emotion_scores else ("neutral", 1.0)

    # 💬 Generate English bot response
    english_response = generate_response(primary_emotion, translated_input)

    # 🔁 Translate response back to original language if needed
    final_response = translate(english_response, target=original_lang) if original_lang != "en" else english_response

    # 🧠 Save chat to session and DB
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
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

