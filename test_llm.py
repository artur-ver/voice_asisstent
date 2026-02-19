import requests
import json
import time

# Конфигурация
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def test_llm():
    print(f"🔄 Проверка подключения к Ollama ({OLLAMA_URL})...")
    
    # 1. Проверка доступности сервера
    try:
        # Ollama обычно отвечает на корневой URL или /api/tags
        requests.get("http://localhost:11434/")
        print("✅ Сервер Ollama доступен.")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удалось подключиться к Ollama.")
        print("Убедитесь, что приложение Ollama запущено!")
        return

    # 2. Проверка наличия модели
    print(f"\n🔄 Проверка модели '{MODEL_NAME}'...")
    try:
        tags_response = requests.get("http://localhost:11434/api/tags")
        if tags_response.status_code == 200:
            models = [m['name'] for m in tags_response.json().get('models', [])]
            print(f"Доступные модели: {models}")
            
            # Проверяем, есть ли наша модель (или версия с тегом :latest)
            if MODEL_NAME not in models and f"{MODEL_NAME}:latest" not in models:
                print(f"⚠️ Внимание: Модель '{MODEL_NAME}' не найдена в списке.")
                print(f"Попробуйте выполнить команду: ollama pull {MODEL_NAME}")
            else:
                print(f"✅ Модель '{MODEL_NAME}' найдена.")
    except Exception as e:
        print(f"⚠️ Не удалось получить список моделей: {e}")

    # 3. Тестовый запрос
    print(f"\n🔄 Отправка тестового запроса к '{MODEL_NAME}'...")
    prompt = "Привет! Как твои дела? Ответь кратко."
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    start_time = time.time()
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "")
            print(f"✅ Ответ получен за {end_time - start_time:.2f} сек:")
            print("-" * 20)
            print(answer)
            print("-" * 20)
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Ошибка при запросе: {e}")

if __name__ == "__main__":
    test_llm()
    input("\nНажмите Enter, чтобы выйти...")
