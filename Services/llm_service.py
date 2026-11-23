from langchain_ollama import ChatOllama


def load_llm_llama():
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

def load_llm_mistral():
    '''
    rol system: define la personalidad, y reglas, es el contexto mas fuerte, es como programar el cerebro
    rol user: define la entrada del usuario
    rol assistant: define la salida del asistente
    '''
    return ChatOllama(
        model="mistral:7b",
        temperature=0.7,
        top_p=0.95
    )

def load_llm_qwen():
    '''
    rol system: define la personalidad, y reglas, es el contexto mas fuerte, es como programar el cerebro
    rol user: define la entrada del usuario
    rol assistant: define la salida del asistente
    '''
    return ChatOllama(
        model="qwen3",
        temperature=0.7,
        top_p=0.95
    )

