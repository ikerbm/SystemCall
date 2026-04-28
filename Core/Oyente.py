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

        self.wake_word = "rafael"

        print("cargando modelo whisper...")
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def escuchar_wake_word(self):
        with sr.Microphone(sample_rate= 16000) as source:
            print ("Esperando palabra clave ")

            while True:
                self.recognizer.adjust_for_ambient_noise(source, duration = 1)
                audio = self.recognizer.listen(source,
                                               timeout=None,
                                               phrase_time_limit=4)

                try:
                    texto = self.audio_a_texto(audio)  # Español porque los comandos estan asi
                    print("Has dicho:", texto)
                    if texto and self.wake_word in texto:
                        Rafael().Voz_del_mundo("Me llamaste?")
                        return True
                except sr.UnknownValueError:
                    pass


    def escuchar_comando(self):
         # 16kHz es ideal para reconocimiento de voz.
        with sr.Microphone(sample_rate=16000) as source:
            print("Escuchando ...")
            audio = self.recognizer.listen(source,
                                           timeout=10,# espera maxima antes de hablar
                                            phrase_time_limit= 6 # tiempo maximo de frase
            )

        try:
            texto = self.audio_a_texto(audio)  # Español porque los comandos estan asi
            print("Has dicho:", texto)
            return texto

        except sr.UnknownValueError:
            return ""

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