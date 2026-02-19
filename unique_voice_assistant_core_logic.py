import listener
import brain
import speaker
import time

def main():
    # 1. Инициализация голоса
    engine = speaker.init_engine()
    speaker.speak("Система запускается...", engine)

    # 2. Инициализация слуха
    try:
        recognizer, mic_source = listener.init_listener()
    except Exception as e:
        print(f"Критическая ошибка микрофона: {e}")
        return

    speaker.speak("Я готов. Говорите.", engine)

    # Команды для выключения/сна (дублируем логику, чтобы ассистент сам тоже мог понять, что ему пора спать)
    # Но основной контроль теперь у менеджера.
    # Оставим тут только реакцию на "пока" или "до свидания" для вежливости,
    # но жесткое убийство процесса будет делать manager.py
    
    # 3. Основной цикл: Слушать -> Думать -> Говорить
    while True:
        try:
            # --- ЭТАП 1: СЛУШАТЬ ---
            # Слушаем, пока не услышим что-то внятное
            text = listener.listen(recognizer, mic_source)
            
            if text:
                print(f"[DEBUG] Распознано: {text}")
                
                # --- ЭТАП 2: ДУМАТЬ ---
                
                # Доп. проверка: игнорировать слишком короткие/шумовые фразы
                if len(text) < 3: 
                    continue

                response = brain.query_llm(text)
                
                # Проверка на файлы
                save_msg = brain.save_file_from_response(response)
                if save_msg:
                    speaker.speak(save_msg, engine)
                
                # --- ЭТАП 3: ГОВОРИТЬ ---
                speaker.speak(response, engine)
                
                # После того как сказали, цикл начинается заново -> снова "Слушать"
                
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка в цикле: {e}")
            time.sleep(1)
                
                # Доп. проверка: игнорировать слишком короткие/шумовые фразы
                if len(text) < 3: 
                    continue

                response = brain.query_llm(text)
                
                # Проверка на файлы
                save_msg = brain.save_file_from_response(response)
                if save_msg:
                    speaker.speak(save_msg, engine)
                
                # --- ЭТАП 3: ГОВОРИТЬ ---
                speaker.speak(response, engine)
                
                # После того как сказали, цикл начинается заново -> снова "Слушать"
                
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка в цикле: {e}")
            time.sleep(1)

    # Очистка ресурсов при выходе
    listener.close_listener(mic_source)

if __name__ == "__main__":
    main()
