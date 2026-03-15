import speech_recognition as sr
from .Rafael import Rafael


class Oyente:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8 #Esto define cuánto silencio indica que terminaste de hablar.

    def escuchar_comando(self):
         # 16kHz es ideal para reconocimiento de voz.
        with sr.Microphone(sample_rate=16000) as source:
            print("Calibrando ruido ambiente...")
            self.recognizer.adjust_for_ambient_noise(source, duration= 1)  # Para filtrar ruido de fondo

            print("Escuchando ...")
            audio = self.recognizer.listen(source,
                                           timeout=10,# espera maxima antes de hablar
                                            phrase_time_limit= 6 # tiempo maximo de frase
            )

        try:
            texto = self.recognizer.recognize_google(audio, language="es-ES")  # Español porque los comandos estan asi
            print("Has dicho:", texto)
            return texto.lower()

        except sr.UnknownValueError:
            mensaje = "No se entendió el comando."
            return ""
        except sr.RequestError as e:
            mensaje = "Error al conectar con el servicio de reconocimiento."
            Rafael().Voz_del_mundo(mensaje)
        return None
