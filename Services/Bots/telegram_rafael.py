import telebot
import os
from dotenv import load_dotenv
from Core.Rafael import Rafael

# Cargar variables de entorno
load_dotenv()

rafael = Rafael()
# Tu token que te da el BotFather en Telegram
bot = telebot.TeleBot(os.getenv("TELEGRAM_API_KEY")) 

@bot.message_handler(func=lambda message: True)
def responder_usuario(message):
    texto_usuario = message.text
    chat_id = str(message.chat.id) # Usamos el ID del chat como identificador único
    
    # Le pasamos el texto a Rafael y usamos el chat_id para separar las memorias
    respuesta = rafael.ask_rafael(texto_usuario, session_id=chat_id)
    print(respuesta)
    
    # Enviamos la respuesta de vuelta por Telegram
    bot.reply_to(message, respuesta)

bot.infinity_polling()
