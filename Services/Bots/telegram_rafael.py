import telebot
import os
import logging
import time
from dotenv import load_dotenv
from Core.Rafael import Rafael


# ==========================================
# Logging
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==========================================
# configuracion
# ==========================================
# Cargar variables de entorno
load_dotenv()

logging.info("Inicializando Rafael...")
rafael = Rafael(use_tts=False)
logging.info("Rafael inicializado correctamente")

# Tu token que te da el BotFather en Telegram
bot = telebot.TeleBot(os.getenv("TELEGRAM_API_KEY"))
# Verificar que Telegram responde y el token es válido
bot_info = bot.get_me()

logging.info(
    f"System Call en línea | @{bot_info.username} listo para recibir mensajes"
)

# ==========================================
# Handlers
# ==========================================
@bot.message_handler(func=lambda message: True)
def responder_usuario(message):
    try:
        texto_usuario = message.text
        chat_id = str(message.chat.id)

        logging.info(
            f"Mensaje recibido de {chat_id}: {texto_usuario}"
        )

        respuesta = rafael.ask_rafael(
            texto_usuario,
            session_id=chat_id
        )

        bot.reply_to(message, respuesta)

        logging.info(
            f"Respuesta enviada a {chat_id}"
        )

    except Exception as e:
        logging.exception(
            f"Error procesando mensaje de {message.chat.id}"
        )

        bot.reply_to(
            message,
            "Lo siento, ocurrió un error procesando tu mensaje."
        )

# ==========================================
# Polling
# ==========================================
while True:
    try:
        logging.info("Iniciando bot de Telegram...")

        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60,
            skip_pending=True
        )

    except Exception as e:
        logging.exception(
            f"Error en polling: {e}"
        )

        logging.info(
            "Reintentando conexión en 10 segundos..."
        )

        time.sleep(10)
