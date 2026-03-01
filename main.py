import asyncio
import os
import sys
from wake_word import WakeWordDetector
from stt import SpeechToText
from llm import LLMClient
from tts import TextToSpeech
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Загружаем стоп-слова из .env
    env_stop_words = os.getenv("STOP_WORDS", "сервер конец")
    stop_words = tuple(word.strip().lower() for word in env_stop_words.split(","))

    # Инициализация компонентов
    try:
        # WakeWordDetector сам загрузит WAKE_WORDS из .env
        ww_detector = WakeWordDetector()
        stt_client = SpeechToText(model_size="small")
        llm_client = LLMClient() # Ожидает GEMINI_API_KEY в .env
        tts_client = TextToSpeech()
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        return

    print("\nГолосовой ассистент запущен!")
    print(f"Кодовые слова для активации: {ww_detector.wake_words}")
    print(f"Команды для остановки: {stop_words}")

    should_listen_prompt = False

    while True:
        if not should_listen_prompt:
            # Ожидание кодового слова
            if ww_detector.listen():
                # Проигрываем приветствие после распознавания кодового слова
                tts_client.play_system_sound("start_server.mp3")
                should_listen_prompt = True
            else:
                continue

        # Запись и распознавание речи
        audio_file = stt_client.record_until_silence()
        # Проигрываем boop после окончания записи
        tts_client.play_system_sound("boop.mp3")
        
        user_text = stt_client.transcribe(audio_file)
        
        if not user_text:
            print("Речь не распознана, возвращаюсь в режим ожидания.")
            should_listen_prompt = False
            continue

        print(f"Вы сказали: {user_text}")

        # Проверка команды остановки
        user_text_lower = user_text.lower()
        is_stop_command = any(stop_word in user_text_lower for stop_word in stop_words)
        
        if is_stop_command:
            print("Команда остановки получена. До свидания!")
            should_listen_prompt = False
            continue

        # Генерация ответа через LLM
        print("Нейросеть думает...")
        try:
            # Теперь вызов асинхронный
            response_text = await llm_client.generate_response(user_text)
            print(f"AI: {response_text}")
        except Exception as e:
            print(f"Ошибка LLM: {e}")
            response_text = "Простите, произошла ошибка при запросе к нейросети."

        # Озвучка ответа
        print("Озвучиваю ответ...")
        response_file = await tts_client.speak_and_get_file(response_text)
        
        # Проигрывание с поддержкой прерывания
        interrupted = tts_client.play_audio(response_file)
        
        if interrupted:
            # Если прервали, сразу переходим к записи нового промпта
            should_listen_prompt = True
            print("Слушаю новый промпт...")
        else:
            # Если дослушали до конца, ждем кодовое слово снова
            should_listen_prompt = False
            print(f"Жду кодовое слово {ww_detector.wake_words}...")

if __name__ == "__main__":
    asyncio.run(main())
