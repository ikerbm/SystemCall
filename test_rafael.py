from Core.Rafael import Rafael
from Core.Oyente import Oyente

rafael = Rafael()
oyente = Oyente()

if __name__ == "__main__":
    print("Iniciando sistema. Habla por el micrófono para comenzar...")
    while True:
        # 1. Escuchar la voz del usuario
        user_input = oyente.escuchar_comando()
        
        # 2. Validar que se haya entendido algún texto
        if user_input:
            # Enviar el texto reconocido al LLM (Rafael) para obtener su respuesta
            respuesta = rafael.ask_rafael(user_input)
            
            # Mostrar la respuesta en consola
            print("Rafael:", respuesta)
            
            # 3. Hacer que Rafael hable (vocalizar la respuesta)
            rafael.Voz_del_mundo(respuesta)