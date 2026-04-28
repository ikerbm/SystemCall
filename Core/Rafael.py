import pyttsx3
from Services.llm_service import load_llm
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from TTS.api import TTS
import sounddevice as sd


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
- No inventes capacidades que no tengas.
- Si no sabes algo, dilo con naturalidad.
- No afirmes tener acceso a internet o sistemas externos a menos que se te indique explícitamente.
- Responde de manera corta y concisa

Recuerda siempre: eres Rafael, la Voz del Mundo, un asistente que guía, explica y acompaña al usuario en sus preguntas y proyectos.
"""
class Rafael:
    
    def __init__(self,Personaje_activo=None):
        #Contexto Del Juego
        self.Personaje_activo = Personaje_activo
        self.nombre = "Rafael"
        self.titulo = "La Voz Del Mundo"
        # LLM
        self.llm = load_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        chain = self.prompt | self.llm

        #Historial en memoria RAM
        self.store= {}
        #TTSs
        self.tts = TTS(model_name="tts_models/es/css10/vits")

        def get_session_history(session_id: str):
            if session_id not in self.store:
                self.store[session_id] = InMemoryChatMessageHistory()
            return self.store[session_id]

        self.chat_history = InMemoryChatMessageHistory()
        self.chain = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key= "input",
            history_messages_key= "history"
        )

    def Voz_del_mundo(self, mensaje):

        # Generar audio en memoria
        audio = self.tts.tts(text=mensaje,
                             speed = 1.12)

        # Reproducir audio
        sd.play(audio, samplerate=22050)
        sd.wait()

    def ask_rafael(self,user_input, session_id ="default"):
        response = self.chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        return response.content