import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

from Core.Rafael import Rafael

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = Flask(__name__)

# Instancia central de Rafael (sin TTS de audio para respuestas de texto rápidas vía API)
logging.info("Inicializando Rafael para la API Web...")
rafael = Rafael(use_tts=False)
logging.info("Rafael listo para atender peticiones web.")

# Middleware de CORS para permitir conexiones desde Vite local (puerto 3000/5173) o GitHub Pages
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

@app.route("/api/status", methods=["GET", "OPTIONS"])
def status():
    if request.method == "OPTIONS":
        return "", 204
    return jsonify({
        "status": "online",
        "assistant": "Rafael",
        "version": "2.5",
        "model": "claude-haiku-5-5"
    })

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", "web_default")

    if not message:
        return jsonify({"error": "No se proporcionó un mensaje."}), 400

    logging.info(f"[API Web] Mensaje recibido (sesión: {session_id}): {message}")

    try:
        respuesta = rafael.ask_rafael(message, session_id=session_id)
        logging.info(f"[API Web] Respuesta generada exitosamente.")
        return jsonify({
            "response": respuesta,
            "status": "ok"
        })
    except Exception as e:
        logging.exception(f"[API Web] Error al procesar mensaje con Rafael: {e}")
        return jsonify({
            "error": "Error interno al procesar el mensaje con el modelo.",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Servidor API de Rafael iniciado en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
