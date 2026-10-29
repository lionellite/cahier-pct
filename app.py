import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"


@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "ANTHROPIC_API_KEY n'est pas configurée sur le serveur."}), 500

    data = request.get_json(force=True, silent=True) or {}
    system_prompt = data.get("system", "")
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message manquant."}), 400

    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        text_blocks = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        answer = "\n".join(text_blocks) if text_blocks else "Aucune réponse reçue."
        return jsonify({"answer": answer})
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        return jsonify({"error": f"Erreur API Anthropic ({resp.status_code})", "detail": detail}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erreur réseau : {str(e)}"}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
