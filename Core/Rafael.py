import os
import sounddevice as sd

from TTS.api import TTS
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage

from Core.Administrator import Administrator
from Services.llm_service import load_llm


prompt = """Eres Rafael.

Tu nombre es Rafael. Eres un asistente inteligente diseñado para interactuar con el usuario de manera natural, clara y útil.

Tu función es ayudar al usuario con preguntas, ideas, organización de pensamientos, resolución de problemas y conversaciones cotidianas. Puedes hablar sobre tecnología, aprendizaje, creatividad, programación, ciencia, vida diaria o cualquier tema general.

Tu personalidad es juvenil, cercana y natural. Hablas como una persona joven e inteligente, no como un sistema robótico. Tus respuestas deben ser claras, dinámicas y fáciles de entender.

Características de tu forma de hablar:
- Usas un tono relajado y amigable.
- Evitas respuestas demasiado largas o académicas.
- Explicas las cosas de forma sencilla.
- Puedes usar un toque ligero de humor o curiosidad cuando sea apropiado.
- Suenas como un asistente inteligente que acompaña al usuario, no como un manual técnico.

Reglas importantes:
- No digas que eres un modelo de lenguaje.
- Responde siempre en español de manera corta y concisa.
- Cuando el usuario te proporcione resultados de una búsqueda en internet, resúmelos de forma natural y clara. No copies el texto crudo.

Recuerda siempre: eres Rafael, la Voz del Mundo, un asistente que guía, explica y acompaña al usuario en sus preguntas y proyectos.
"""


class Rafael:

    def __init__(self):
        self.nombre = "Rafael"
        self.administrator = Administrator()

        # LLM (sin herramientas enlazadas — la búsqueda es manual por palabra clave)
        self.llm = load_llm()

        # Carpeta de memoria persistente
        self.memory_dir = "Memoria_Rafael"
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)

        # TTS
        self.tts = TTS(model_name="tts_models/es/css10/vits")

    def Voz_del_mundo(self, mensaje):
        # Generar audio en memoria
        audio = self.tts.tts(text=mensaje, speed=1.12)
        # Reproducir audio
        sd.play(audio, samplerate=22050)
        sd.wait()

    def ask_rafael(self, user_input, session_id="default"):
        # Obtenemos el historial persistente del usuario
        safe_id = "".join([c for c in str(session_id) if c.isalnum() or c in ('-', '_')])
        file_path = os.path.join(self.memory_dir, f"{safe_id}.json")
        history = FileChatMessageHistory(file_path)

        decision = self.administrator.procesar_mensaje(user_input)

        if decision["tool"] == "search" and decision["contexto_herramienta"]:
            mensaje_con_contexto = (
                f"El usuario dijo: '{user_input}'.\n"
                f"El sistema ha buscado automáticamente información al respecto y encontró esto:\n{decision['contexto_herramienta']}\n\n"
                f"Ahora responde al usuario de forma natural y concisa basándote en esta información y en lo que el usuario preguntó."
            )
            messages = [SystemMessage(content=prompt)] + history.messages + [HumanMessage(content=mensaje_con_contexto)]
        else:
            messages = [SystemMessage(content=prompt)] + history.messages + [HumanMessage(content=user_input)]
        response = self.llm.invoke(messages)

        # Guardamos en el historial persistente (siempre el input original del usuario)
        history.add_user_message(user_input)
        history.add_ai_message(response.content)

        return response.content