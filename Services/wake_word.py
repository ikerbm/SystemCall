import pvporcupine
import pyaudio
import struct


class WakeWordDetector:

    def __init__(self, access_key = "nXQdCa8BbYyi71d/Q3YiSVWofKzeyZG4sr4qF7QgnC3+HXkwBKSdOA=="):

        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["porcupine"]  # temporal
        )

        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def escuchar(self):

        print("Esperando wake word...")

        while True:

            pcm = self.stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            result = self.porcupine.process(pcm)

            if result >= 0:
                print("Wake word detectada")
                return True