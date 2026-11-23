from faster_whisper import WhisperModel
import speech_recognition as sr
import tempfile
from .Rafael import Rafael


class Oyente:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8 #Esto define cuánto silencio indica que terminaste de hablar.

        print("cargando modelo whisper...")
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def escuchar_comando(self):
         # 16kHz es ideal para reconocimiento de voz.
        with sr.Microphone(sample_rate=16000) as source:
            print("Escuchando ...")
            try: 
                audio = self.recognizer.listen(source,
                                           timeout=10,# espera maxima antes de hablar
                                            phrase_time_limit= 6 # tiempo maximo de frase
                )

        
                texto = self.recognizergnize_google(audio, language="es-ES")  # Español porque los comandos estan asi
                print("Has dicho:", texto)
                return texto

            except sr.WaitTimeoutError:
                print("No detecté ninguna voz.")
                return None

            except sr.UnknownValueError:
                print("No pude entender lo que dijiste.")
                return None

            except sr.RequestError as e:
                print(f"Error del servicio de reconocimiento: {e}")
                return None

    def audio_a_texto(self, audio):

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio.get_wav_data())

            segments, info = self.model.transcribe(
                temp_audio.name,
                language="es",
                beam_size=5
            )

        texto = ""

        for segment in segments:
            texto += segment.text

        return texto.lower().strip()