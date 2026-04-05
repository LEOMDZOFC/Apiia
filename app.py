from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- Configuração ---
SAMBA_API_KEY = "628081f7-96e9-4bf1-a467-488a2f33284c"
SAMBA_URL = "https://api.sambanova.ai/v1/chat/completions"
LOCAL_API_KEY = "LEOMODZ"  # Sua chave local

@app.route("/ask", methods=["GET"])
def ask_sambanova():
    # Obtém parâmetros
    message = request.args.get("message")
    key = request.args.get("key")
    
    # Valida chave local
    if key != LOCAL_API_KEY:
        return jsonify({"error": "Invalid API Key!"}), 401

    if not message:
        return jsonify({"error": "Missing 'message' parameter!"}), 400

    headers = {
        "Authorization": f"Bearer {SAMBA_API_KEY}",
        "Content-Type": "application/json",
    }

    # Payload atualizado com modelo existente
    payload = {
        "model": "DeepSeek-R1-0528",  # modelo válido
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": message}
        ],
        "temperature": 0.1,
        "top_p": 0.1
    }

    try:
        response = requests.post(SAMBA_URL, headers=headers, json=payload, timeout=30)

        # Se status HTTP não for 200, retorna erro com texto
        if response.status_code != 200:
            return jsonify({
                "error": f"SambaNova API returned status {response.status_code}",
                "response_text": response.text
            }), 500

        # Tenta decodificar JSON
        try:
            data = response.json()
        except Exception:
            return jsonify({
                "error": "Failed to decode JSON from SambaNova API",
                "response_text": response.text
            }), 500

        # Extrai resposta do modelo
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No response from model.")

        return jsonify({
            "status": "success",
            "message": message,
            "reply": reply
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"Starting AI-API on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)