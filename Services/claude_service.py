from langchain_anthropic import ChatAnthropic

def load_llm_claude():
    '''
    rol system: define la personalidad, y reglas, es el contexto mas fuerte, es como programar el cerebro
    rol user: define la entrada del usuario
    rol assistant: define la salida del asistente
    '''
    return ChatAnthropic(
        model="claude-haiku-5-5",
        max_tokens=1024,
    )