import pyttsx3
import sys

def speak_loop():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        ru_voice = None
        for voice in voices:
            if 'ru' in voice.id.lower() or 'russian' in voice.name.lower() or 'rus' in voice.name.lower():
                ru_voice = voice.id
                break
        
        if ru_voice:
            engine.setProperty('voice', ru_voice)
        engine.setProperty('rate', 180)
        
        # Читаем из stdin и озвучиваем
        for line in sys.stdin:
            text = line.strip()
            if text:
                try:
                    engine.say(text)
                    engine.runAndWait()
                except:
                    pass
    except:
        pass

if __name__ == "__main__":
    speak_loop()