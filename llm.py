import os
from google import genai
from dotenv import load_dotenv
import g4f
import asyncio

load_dotenv()

class LLMClient:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("Предупреждение: API ключ Gemini не найден. Gemini будет доступен только как вторичный fallback (если g4f не сработает).")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Ошибка при инициализации Gemini: {e}")
                self.client = None
        
        self.model_name = model_name
        # Системная инструкция для краткости
        self.system_instruction = "Отвечай максимально кратко и лаконично, буквально одной фразой или парой слов."

    async def generate_response(self, prompt):
        """Генерирует ответ на основе запроса асинхронно с инструкцией краткости."""
        
        # Объединяем системную инструкцию с запросом пользователя
        full_prompt = f"{self.system_instruction}\n\nПользователь: {prompt}"
        
        # 1. Попытка использовать основную нейросеть (g4f)
        print("Использую основную нейросеть (g4f)...")
        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": full_prompt}],
            )
            if response:
                return str(response).strip()
        except Exception as e:
            print(f"Ошибка основной нейросети (g4f): {e}. Переключаюсь на Gemini...")

        # 2. Резервный вариант: Google Gemini
        if self.client:
            models_to_try = [self.model_name, "gemini-1.5-flash", "gemini-2.0-flash-exp"]
            
            for model in models_to_try:
                try:
                    response = await self.client.aio.models.generate_content(
                        model=model,
                        contents=full_prompt
                    )
                    return response.text.strip()
                except Exception as e:
                    error_str = str(e).upper()
                    if "API_KEY_INVALID" in error_str or "INVALID_ARGUMENT" in error_str:
                        print("Критическая ошибка: API ключ Gemini невалиден.")
                        self.client = None
                        break
                    print(f"Gemini ({model}) ошибка: {e}. Пробую альтернативы...")
                    continue

        return "Простите, все нейросети сейчас недоступны."
