import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Get OpenRouter API Key
api_key = os.getenv("OPENROUTER_API_KEY")

@app.route("/")
def home():
    return "DeepSeek AI agent is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-v3",
        "messages": [{"role": "user", "content": message}]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No reply")
        return jsonify({"reply": answer})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
