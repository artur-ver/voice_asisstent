import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

load_dotenv()

class WakeWordDetector:
    def __init__(self, wake_words=None):
        # Загружаем слова из .env, если они не переданы явно
        if wake_words is None:
            env_words = os.getenv("WAKE_WORDS", "сервер")
            # Превращаем строку "слово1,слово2" в кортеж ("слово1", "слово2")
            self.wake_words = tuple(word.strip().lower() for word in env_words.split(","))
        else:
            self.wake_words = tuple(word.lower() for word in wake_words)

        print("Загрузка модели Vosk для распознавания кодового слова...")
        self.model = Model(lang="ru")
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def listen(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        print(f"Слушаю кодовые слова: {self.wake_words}...")
        
        try:
            while True:
                data = stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    break
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    # Проверяем наличие любого из кодовых слов в тексте
                    for word in self.wake_words:
                        if word in text:
                            print(f"Кодовое слово '{word}' распознано!")
                            return True
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "")
                    for word in self.wake_words:
                        if word in partial_text:
                            print(f"Кодовое слово '{word}' распознано (частично)!")
                            return True
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
        return False
