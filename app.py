from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests  # Import requests to call Ollama API
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the frontend directory
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '../frontend')

# Serve the frontend files
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

        # Call DeepSeek-R1 8B running on Ollama
        ollama_response = requests.post(
            "http://localhost:11436/api/generate",  # Updated port
            json={"model": "deepseek-r1:7b", "prompt": user_message, "stream": False},
            timeout=30
            
        )

        if ollama_response.status_code != 200:
            logger.error(f"Failed to connect to DeepSeek-R1 8B: {ollama_response.text}")
            return jsonify({"error": "Failed to connect to DeepSeek-R1 8B"}), 500

        response_json = ollama_response.json()
        bot_message = response_json.get("response", "Error: No response from DeepSeek-R1 8B")

        logger.info(f"Bot response: {bot_message}")
        return jsonify({"message": bot_message})

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": f"Request to DeepSeek-R1 8B failed: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
