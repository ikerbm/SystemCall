import speech_recognition as sr
from .Rafael import Rafael


class Oyente:
    def __init__(self):
        self.nombre = "Dumbo"
        self.titulo = "El Oyente" 

    def escuchar_comando(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Escuchando...")
            recognizer.adjust_for_ambient_noise(source)  # Para filtrar ruido de fondo
            audio = recognizer.listen(source)

        try:
            texto = recognizer.recognize_google(audio, language="es-ES")  # Español porque los comandos estan asi
            print("Has dicho:", texto)
            return texto
        except sr.UnknownValueError:
            mensaje = "No se entendió el comando."
            #Rafael().Voz_del_mundo(mensaje)
            return ""
            #print("No se entendió el audio.")
        except sr.RequestError as e:
            mensaje = "Error al conectar con el servicio de reconocimiento."
            Rafael().Voz_del_mundo(mensaje)
            #print(f"Error al conectar con el servicio de reconocimiento: {e}")

        return None
