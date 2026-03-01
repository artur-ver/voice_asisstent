import asyncio
import edge_tts
import sounddevice as sd
import numpy as np
import threading
import webrtcvad
import os
import pygame

class TextToSpeech:
    def __init__(self, voice="ru-RU-SvetlanaNeural"):
        self.voice = voice
        self.is_playing = False
        self.interrupt_event = threading.Event()
        self.vad = webrtcvad.Vad(3)
        self.sample_rate = 16000
        pygame.mixer.init()

    async def speak_and_get_file(self, text, output_file="response.mp3"):
        """Преобразует текст в речь и сохраняет в файл."""
        # Освобождаем файл перед записью, если он занят pygame
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception:
            pass

        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
        return output_file

    def play_audio(self, file_path):
        """Проигрывает аудиофайл и проверяет на прерывание."""
        self.is_playing = True
        self.interrupt_event.clear()

        # Start monitoring for interruption
        interruption_thread = threading.Thread(target=self._monitor_interruption)
        interruption_thread.daemon = True
        interruption_thread.start()

        # Play with pygame
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for end or interruption
            while pygame.mixer.music.get_busy() and not self.interrupt_event.is_set():
                pygame.time.Clock().tick(10)
            
            if self.interrupt_event.is_set():
                pygame.mixer.music.stop()
                print("Озвучка прервана голосом.")
                return True
        except Exception as e:
            print(f"Ошибка при воспроизведении: {e}")
        finally:
            self.is_playing = False
            # Пытаемся освободить файл сразу после завершения
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
        
        return False

    def play_system_sound(self, sound_path):
        """Проигрывает системный звук (без прерывания)."""
        if not os.path.exists(sound_path):
            return
        try:
            # Используем Sound для коротких звуков, чтобы не мешать музыке
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
            # Ждем окончания (звук короткий)
            pygame.time.wait(int(sound.get_length() * 1000))
        except Exception as e:
            print(f"Ошибка при проигрывании системного звука: {e}")

    def _monitor_interruption(self, frame_duration=30):
        """Слушает микрофон во время озвучки и устанавливает событие прерывания, если обнаружен голос."""
        frame_size = int(self.sample_rate * frame_duration / 1000)
        
        def callback(indata, frames, time, status):
            if not self.is_playing:
                return
            
            # Convert to int16 for webrtcvad
            audio_data = (indata * 32768).astype(np.int16).tobytes()
            
            # Check if it's speech
            try:
                if self.vad.is_speech(audio_data, self.sample_rate):
                    self.interrupt_event.set()
            except Exception as e:
                pass

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32', blocksize=frame_size, callback=callback):
            while self.is_playing and not self.interrupt_event.is_set():
                sd.sleep(100)
