import json
import requests

SAMBA_API_KEY = "628081f7-96e9-4bf1-a467-488a2f33284c"
SAMBA_URL = "https://api.sambanova.ai/v1/chat/completions"
LOCAL_API_KEY = "LEOMODZDEV"  # Sua chave local

def handler(req):
    # req.query é um dict com os parâmetros GET
    query = req.get("query", {})
    message = query.get("message")
    key = query.get("key")

    # Valida chave
    if key != LOCAL_API_KEY:
        return {"statusCode": 401, "body": json.dumps({"error": "Invalid API Key!"})}

    if not message:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing 'message' parameter!"})}

    payload = {
        "model": "DeepSeek-R1-0528",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": message}
        ],
        "temperature": 0.1,
        "top_p": 0.1
    }

    headers = {
        "Authorization": f"Bearer {SAMBA_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(SAMBA_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": f"SambaNova API returned status {response.status_code}",
                    "response_text": response.text
                })
            }

        try:
            data = response.json()
        except Exception:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "Failed to decode JSON from SambaNova API",
                    "response_text": response.text
                })
            }

        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No response from model.")
        if "</think>" in reply:
            reply = reply.split("</think>")[-1].strip()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message": message,
                "reply": reply
            })
        }

    except requests.exceptions.RequestException as e:
        return {"statusCode": 500, "body": json.dumps({"error": f"Request error: {str(e)}"})}