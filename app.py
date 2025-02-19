from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import requests  # Import requests to call Ollama API
import logging
import json

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

        # System prompt to ensure only Indian judiciary-related queries are answered
        system_prompt = "You are an AI assistant specialized in Indian judiciary and related legal matters. Only answer questions related to Indian judiciary, laws, and legal procedures. If the question is outside this scope, respond with 'This question is outside my area of expertise.'"
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"

        # Call DeepSeek-R1 8B running on Ollama with streaming
        ollama_response = requests.post(
            "http://localhost:11436/api/generate",  # Updated port
            json={"model": "deepseek-r1:7b", "prompt": full_prompt, "stream": True},
            stream=True
        )

        if ollama_response.status_code != 200:
            logger.error(f"Failed to connect to DeepSeek-R1 8B: {ollama_response.text}")
            return jsonify({"error": "Failed to connect to DeepSeek-R1 8B"}), 500

        def generate():
            for chunk in ollama_response.iter_lines():
                if chunk:
                    # Decode the chunk and parse it as JSON
                    decoded_chunk = chunk.decode('utf-8')
                    try:
                        chunk_json = json.loads(decoded_chunk)
                        response_text = chunk_json.get("response", "")
                        
                        # Remove <think> tags from the response
                        response_text = response_text.replace("<think>", "").replace("</think>", "")
                        
                        logger.info(f"Streaming chunk: {response_text}")
                        yield response_text
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode JSON chunk: {e}")
                        yield ""

        # Stream the response to the client
        return Response(generate(), content_type='text/plain')

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": f"Request to DeepSeek-R1 8B failed: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
