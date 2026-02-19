import speech_recognition as sr
import subprocess
import sys
import os
import time
import signal
from listener import SoundDeviceMicrophone
import psutil

# Глобальная переменная для процесса ассистента
assistant_process = None

def kill_process_tree(pid):
    """Убивает процесс и всех его детей"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def start_assistant():
    """Запускает main.py как отдельный процесс"""
    global assistant_process
    
    # Если процесс жив, ничего не делаем
    if assistant_process and assistant_process.poll() is None:
        print("⚠️ Ассистент уже работает.")
        return

    print("\n🚀 ЗАПУСК АССИСТЕНТА...")
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), 'unique_voice_assistant_core_logic.py')
    
    # Запускаем main.py
    assistant_process = subprocess.Popen([python_exe, script_path])

def stop_assistant():
    """Убивает процесс ассистента"""
    global assistant_process
    
    if assistant_process:
        print("\n🛑 ОСТАНОВКА АССИСТЕНТА...")
        try:
            # Убиваем дерево процессов (main.py + speak_process.py)
            kill_process_tree(assistant_process.pid)
            assistant_process = None
            print("✅ Ассистент остановлен.")
        except Exception as e:
            print(f"Ошибка остановки: {e}")
    else:
        print("⚠️ Ассистент не запущен.")

def listen_for_commands():
    """Слушает команды управления сервером"""
    r = sr.Recognizer()
    r.energy_threshold = 2000
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.5 
    
    # Используем наш микрофон
    mic_source = SoundDeviceMicrophone()
    
    # Инициализация контекста микрофона
    mic_source.__enter__()
    
    print("\n🎧 МЕНЕДЖЕР ЗАПУЩЕН. Жду команды: 'Сервер старт' / 'Сервер стоп'")
    
    # Калибровка шума
    r.adjust_for_ambient_noise(mic_source, duration=1.0)
    
    while True:
        try:
            # Слушаем фразы
            # timeout=None -> ждем бесконечно
            # phrase_time_limit=10 -> даем время договорить фразу
            audio = r.listen(mic_source, timeout=None, phrase_time_limit=10)
            
            try:
                # Распознаем
                text = r.recognize_google(audio, language="ru-RU").lower()
                print(f"[MANAGER]: {text}")
                
                # Синонимы для "сервер" (часто путает)
                TRIGGERS = ["сервер", "север", "сэр", "сир", "сергей", "эссистент", "бот"]
                
                # Команды запуска
                START_WORDS = ["старт", "привет", "проснись", "включись", "работа", "вставай", "запуск"]
                
                # Команды остановки
                STOP_WORDS = ["стоп", "хватит", "заткнись", "тихо", "молчать", "выключись", "отключись", "спать"]

                # Проверка: есть ли триггер в тексте?
                has_trigger = any(t in text for t in TRIGGERS)
                
                # Проверка: есть ли команда старта?
                has_start = any(s in text for s in START_WORDS)
                
                # Проверка: есть ли команда стопа?
                has_stop = any(s in text for s in STOP_WORDS)
                
                if has_trigger and has_start:
                    start_assistant()
                    
                elif (has_trigger and has_stop) or (any(sw in text for sw in ["стоп", "заткнись", "тихо"]) and len(text.split()) < 3): 
                    # Если просто сказали "стоп" или "заткнись" (короткая фраза), тоже можно останавливать
                    stop_assistant()
                    
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                # print("Ошибка сети")
                pass
                
        except KeyboardInterrupt:
            stop_assistant()
            print("\nВыход из менеджера.")
            break
        except Exception as e:
            print(f"Ошибка менеджера: {e}")
            time.sleep(1)
    
    # Закрываем микрофон при выходе
    mic_source.__exit__(None, None, None)

if __name__ == "__main__":
    listen_for_commands()