from langchain_ollama import ChatOllama


def load_llm():
    '''
    rol system: define la personalidad, y reglas, es el contexto mas fuerte, es como programar el cerebro
    rol user: define la entrada del usuario
    rol assistant: define la salida del asistente
    '''
    return ChatOllama(
        model="llama3.1:8b",
        temperature=0.7,
        top_p=0.95
    )
