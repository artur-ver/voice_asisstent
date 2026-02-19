import speech_recognition as sr
import sounddevice as sd
import numpy as np

# Классы для работы с sounddevice (вместо pyaudio)
class SoundDeviceStream:
    """Обертка для потока sounddevice, совместимая с speech_recognition"""
    def __init__(self, stream):
        self.stream = stream
    
    def read(self, size):
        frames = size // 2 
        data, overflow = self.stream.read(frames)
        return bytes(data)
        
    def close(self):
        self.stream.stop()
        self.stream.close()

class SoundDeviceMicrophone(sr.AudioSource):
    """Микрофон на базе sounddevice"""
    def __init__(self, device=None, sample_rate=16000, chunk_size=1024):
        self.device = device
        self.SAMPLE_RATE = sample_rate
        self.CHUNK = chunk_size
        self.SAMPLE_WIDTH = 2 
        self.stream = None

    def __enter__(self):
        self.raw_stream = sd.RawInputStream(
            samplerate=self.SAMPLE_RATE,
            blocksize=self.CHUNK,
            device=self.device,
            channels=1,
            dtype='int16',
            callback=None 
        )
        self.raw_stream.start()
        self.stream = SoundDeviceStream(self.raw_stream)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.close()
        self.raw_stream.close()

def init_listener():
    """Инициализация и калибровка микрофона"""
    r = sr.Recognizer()
    r.energy_threshold = 2000 
    r.dynamic_energy_threshold = True
    r.pause_threshold = 4.0 # Ждем 4 секунды тишины, как просил пользователь
    
    # Открываем микрофон один раз
    source = SoundDeviceMicrophone()
    
    # Инициализируем поток
    source.__enter__()
    
    print("🔊 Настройка микрофона под уровень шума... (помолчите 1 секунду)")
    # Для adjust_for_ambient_noise нужен source
    r.adjust_for_ambient_noise(source, duration=1.0)
    print("✅ Микрофон настроен.")
    
    return r, source

def listen(r, source):
    """Слушает одну фразу и возвращает текст"""
    try:
        print("🎤 Слушаю... (говорите)")
        
        # Слушаем до конца фразы
        # timeout=None -> ждем бесконечно начала речи
        # phrase_time_limit=None -> не обрываем фразу (ждем pause_threshold)
        audio = r.listen(source, timeout=None, phrase_time_limit=None)
        
        print("⏳ Распознаю...")
        try:
            text = r.recognize_google(audio, language="ru-RU")
            print(f"[ПОЛЬЗОВАТЕЛЬ]: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return "" # Не разобрал
        except sr.RequestError:
            print("🔴 Ошибка подключения к Google Speech Recognition")
            return ""
            
    except Exception as e:
        print(f"🔴 Ошибка микрофона: {e}")
        return ""

def close_listener(source):
    """Закрытие потока микрофона"""
    if source:
        source.__exit__(None, None, None)
