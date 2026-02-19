import requests
import json

# Конфигурация
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def query_llm(prompt):
    """Отправляет запрос к локальной LLM через Ollama"""
    print(f"\n🧠 Думаю... ({MODEL_NAME})")
    
    # Системная инструкция для модели
    system_prompt = (
        "Ты — голосовой ассистент. Отвечай на русском языке МАКСИМАЛЬНО КРАТКО и ПО СУТИ.\n"
        "Ограничь ответы 1-2 предложениями, если это возможно.\n"
        "Не используй вводные фразы типа 'Конечно', 'Вот ответ'.\n"
        "Если тебя просят написать код, начни ответ строго с 'FILE: <имя_файла>'.\n"
        "Пример кода:\n"
        "FILE: script.py\n"
        "print('Hello')\n"
    )
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Не удалось получить ответ от модели")
        else:
            return f"Ошибка API: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Ошибка подключения к Ollama. Убедитесь, что Ollama запущена."

def save_file_from_response(response):
    """Проверяет, есть ли в ответе файл, и сохраняет его"""
    if "FILE:" in response[:20]: # Проверка в начале строки
        try:
            lines = response.split('\n')
            filename = lines[0].replace("FILE:", "").strip()
            content = '\n'.join(lines[1:])
            
            # Убираем возможные маркдаун-теги
            if content.startswith("```"):
                content = '\n'.join(content.split('\n')[1:])
            if content.endswith("```"):
                content = '\n'.join(content.split('\n')[:-1])
                
            # Сохраняем файл
            import os
            if not os.path.exists("generated_files"):
                os.makedirs("generated_files")
                
            file_path = os.path.join("generated_files", filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            return f"Файл {filename} успешно сохранен."
        except Exception as e:
            return f"Ошибка сохранения файла: {e}"
    return None
