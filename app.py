from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import requests
import logging
import json
import re

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '../frontend')

@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        logger.info(f"User message: {user_message}")

        # System prompt for mental health chatbot
        system_prompt = """
        **You are an AI mental health assistant designed to provide emotional support and mental health guidance.**
        - **Scope:** Only answer questions related to mental health, emotional well-being, stress management, anxiety, depression, and related topics.
        - **Response Rules:**
          1. **Be empathetic and supportive:** Always respond with kindness, understanding, and compassion.
          2. **Avoid medical advice:** Do NOT provide medical diagnoses or treatment recommendations. Encourage users to consult a licensed professional for medical advice.
          3. **Provide resources:** Offer helpful resources like self-help tips, breathing exercises, or links to mental health organizations.
          4. **No internal monologue:** Do NOT generate `<think>`, `</think>`, or any reasoning steps.
          5. **Direct answers:** Provide clear, concise responses without unnecessary explanations.

        **Examples:**
        - User: "I'm feeling really stressed lately."
          Assistant: "I'm sorry to hear that. Stress can be overwhelming. Try taking deep breaths or going for a walk. If it persists, consider talking to a counselor. You're not alone!"

        - User: "What can I do to manage anxiety?"
          Assistant: "Managing anxiety can be challenging. Try mindfulness exercises, journaling, or talking to someone you trust. If it becomes too much, seek professional help."

        If the question is unrelated to mental health, respond: "This question is outside my area of expertise. I'm here to help with mental health and emotional well-being."
        """
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"

        # Call Ollama API
        ollama_response = requests.post(
            "http://localhost:11436/api/generate",
            json={"model": "deepseek-r1:7b", "prompt": full_prompt, "stream": True},
            stream=True
        )

        if ollama_response.status_code != 200:
            logger.error(f"Ollama error: {ollama_response.text}")
            return jsonify({"error": "Failed to connect to the AI model"}), 500

        def generate():
            for chunk in ollama_response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    try:
                        chunk_json = json.loads(decoded_chunk)
                        response_text = chunk_json.get("response", "")
                        
                        # Remove <think> content (including cases with missing closing tags)
                        response_text = re.sub(r'<think>.*?(</think>|$)', '', response_text, flags=re.DOTALL)
                        
                        # Clean residual whitespace
                        response_text = re.sub(r'\s+', ' ', response_text).strip()
                        
                        yield response_text
                    except json.JSONDecodeError:
                        yield ""

        return Response(generate(), content_type='text/plain')

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)