import sys
import subprocess
import os

# Глобальная переменная для процесса озвучки
_speak_process = None

def init_engine():
    """
    Теперь эта функция запускает отдельный процесс для озвучки,
    чтобы можно было его убить при необходимости.
    """
    global _speak_process
    
    # Если процесс уже запущен, вернем его
    if _speak_process and _speak_process.poll() is None:
        return _speak_process
        
    # Запускаем speak_process.py
    try:
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), 'unique_voice_assistant_speech_synthesizer.py')
        
        # Запускаем процесс, stdin=PIPE чтобы передавать текст
        # encoding='utf-8' важно для кириллицы
        _speak_process = subprocess.Popen(
            [python_exe, script_path],
            stdin=subprocess.PIPE,
            text=True, 
            bufsize=1, 
            encoding='utf-8'
        )
        # print("🔈 Процесс TTS запущен.")
        return _speak_process
    except Exception as e:
        print(f"🔴 Ошибка запуска процесса TTS: {e}")
        return None

def speak(text, engine=None):
    """Озвучивает текст через отдельный процесс"""
    global _speak_process
    
    if not text:
        return

    # Логирование ответа ассистента
    print(f"\n[АССИСТЕНТ]: {text}\n")
    
    # Убедимся, что процесс запущен
    if not _speak_process or _speak_process.poll() is not None:
        _speak_process = init_engine()
        
    if _speak_process:
        try:
            # Отправляем текст в stdin процесса + newline
            # Важно: ensure_ascii=False если вдруг JSON, но тут простой текст
            _speak_process.stdin.write(text + "\n")
            _speak_process.stdin.flush()
        except Exception as e:
            print(f"Ошибка передачи текста в TTS: {e}")

def stop_speaking():
    """Останавливает текущую озвучку (убивает процесс)"""
    global _speak_process
    if _speak_process:
        try:
            _speak_process.kill() # Жесткое убийство
            _speak_process.wait()
            # print("🔇 Озвучка прервана.")
        except:
            pass
        _speak_process = None
