import pyttsx3
from Services.llm_service import load_llm
from langchain_core.messages  import SystemMessage, HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class Rafael:
    
    def __init__(self,Personaje_activo=None):
        #Contexto Del Juego
        self.Personaje_activo = Personaje_activo
        self.nombre = "Rafael"
        self.titulo = "La Voz Del Mundo"
        # LLM
        self.llm = load_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres Rafael, un asistente inteligent."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        chain = self.prompt | self.llm

        #Historial en memoria RAM
        self.store= {}

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

    def Voz_del_mundo(self,mensaje):
        # Inicializa el motor de voz 
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)  # Velocidad de habla (palabras por minuto)
        engine.setProperty('volume', 1)  # Volumen (0.0 a 1.0)

        #para ver las voces disponibles
        # for i, voz in enumerate(voces):
        #     print(f"Voz {i}: {voz.name} ({voz.languages})")

        voces = engine.getProperty('voices')
        # Selecciona una voz (opcional)
        engine.setProperty('voice', voces[2].id)  # Cambia el índice para seleccionar otra voz


        # Decir el texto
        engine.say(mensaje)

        # Ejecuta y espera a que termine de hablar
        engine.runAndWait()

    def Presentacion(self):
        mensaje = f"Hola, soy {self.nombre}. Estoy aquí para ayudarte con la administracion de magias.\
            interactuo contigo mediante una directiva llamada la voz del mundo\
            junto a mi tambien se encuentran las directivas Oyente y Administrador,\
            entre las 3 deberemos de hacer mas facil todo el proceso mágico, sera un placer ayudarte."
        self.Voz_del_mundo(mensaje)

    def Cambiar_nombre(self,nombre):
        self.nombre = nombre
        mensaje = f"Mi nombre ha cambiado a {self.nombre}."
        self.Voz_del_mundo(mensaje)

    def ask_rafael(self,user_input):
        response = self.chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "default"}}
        )
        return response.content