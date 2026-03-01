import os
import wave
import pyaudio
import numpy as np
import webrtcvad
from collections import deque
from faster_whisper import WhisperModel

class SpeechToText:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        print(f"Загрузка модели Faster-Whisper '{model_size}'...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.vad = webrtcvad.Vad(3) # 3 is the most aggressive VAD setting

    def record_until_silence(self, sample_rate=16000, frame_duration=30, padding_duration_ms=1000):
        """Записывает звук, пока пользователь говорит, и останавливается при тишине."""
        p = pyaudio.PyAudio()
        num_padding_frames = int(padding_duration_ms / frame_duration)
        ring_buffer = deque(maxlen=num_padding_frames)
        triggered = False
        
        frame_size = int(sample_rate * frame_duration / 1000) # Number of samples in a frame
        
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=frame_size)
        
        print("Слушаю ваш запрос...")
        
        audio_frames = []
        
        while True:
            frame = stream.read(frame_size, exception_on_overflow=False)
            is_speech = self.vad.is_speech(frame, sample_rate)
            
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    print("Голос обнаружен, запись началась.")
                    for f, s in ring_buffer:
                        audio_frames.append(f)
                    ring_buffer.clear()
            else:
                audio_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    print("Тишина обнаружена, запись завершена.")
                    break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to temp file
        temp_filename = "temp_query.wav"
        with wave.open(temp_filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(audio_frames))
        
        return temp_filename

    def transcribe(self, audio_file):
        """Преобразует аудио в текст."""
        segments, info = self.model.transcribe(audio_file, language="ru")
        text = "".join([segment.text for segment in segments])
        return text.strip()
