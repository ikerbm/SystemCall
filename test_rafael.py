from Core.Rafael import Rafael
from Core.Oyente import Oyente
from Services.wake_word import WakeWordDetector

rafael = Rafael()
oyente = Oyente()
wake = WakeWordDetector()


prueba_manual = "rafael, busca en internet el precio del dolar hoy"
probando = True
if __name__ == "__main__":
    print("Iniciando sistema. Habla por el micrófono para comenzar...")
    while True:
        # 1. Escuchar la palabra clave
        if oyente.escuchar_wake_word():
            # 2. Escuchar la voz del usuario
            user_input = oyente.escuchar_comando()

            # 3. Validar que se haya entendido algún texto
            if user_input:
                # Enviar el texto reconocido al LLM (Rafael) para obtener su respuesta
                respuesta = rafael.ask_rafael(user_input)

                # Mostrar la respuesta en consola
                #print("Rafael:", respuesta)

                # 4. Hacer que Rafael hable (vocalizar la respuesta)
                rafael.Voz_del_mundo(respuesta)
        elif probando:
            user_input = prueba_manual
            respuesta = rafael.ask_rafael(user_input)
            rafael.Voz_del_mundo(respuesta)