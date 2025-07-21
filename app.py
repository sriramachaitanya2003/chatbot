from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
import re
import os

# ✅ Updated Flask configuration for static files
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# ✅ Configure Gemini API key
genai.configure(api_key="AIzaSyC0_qSA3FM2g6UdZI5IQETfwjJKT_OfkLI")

# ✅ Load Gemini 2.5 Pro model
model = genai.GenerativeModel("models/gemini-2.5-pro")

# ✅ In-memory conversation history
conversation_history = []

# 🔧 Clean and format as: paragraph + step-by-step points
def format_paragraph_and_steps(text):
    # Remove markdown/special characters (*, #, backticks, etc.)
    clean_text = re.sub(r"[#*`_>\\]", "", text)

    lines = clean_text.strip().split("\n")
    paragraph = []
    steps = []

    for line in lines:
        line = line.strip()
        if re.match(r"^\d+\.\s+", line):
            steps.append(line)
        elif line:
            paragraph.append(line)

    result = ""

    # Add paragraph summary
    if paragraph:
        result += " ".join(paragraph) + "\n\n"

    # Add key points as numbered list
    if steps:
        for step in steps:
            result += step.strip() + "\n"

    return result.strip()

# 💬 Generate reply using Gemini
def generate_reply(user_message):
    global conversation_history, model

    conversation_history.append({"role": "user", "content": user_message})

    # 📌 Instructions to Gemini
    format_instructions = (
        "Please answer the user's question with a short paragraph summary first. "
        "Then provide clear key points in numbered format (1. 2. 3.). "
        "Avoid using special characters like asterisks or markdown. "
        "Return clean, beginner-friendly plain text only.\n"
    )

    prompt = format_instructions
    for msg in conversation_history:
        role = msg["role"].capitalize()
        prompt += f"{role}: {msg['content']}\n"

    response = model.generate_content(prompt)
    bot_reply = response.text.strip()

    conversation_history.append({"role": "assistant", "content": bot_reply})

    return format_paragraph_and_steps(bot_reply)

# ✅ Add route to serve static files explicitly
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message sent"}), 400

    try:
        reply = generate_reply(user_message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)