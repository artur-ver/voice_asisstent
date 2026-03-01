import asyncio
from llm import LLMClient

async def test_llm():
    print("--- ЗАПУСК ТЕСТОВОЙ ВЕРСИИ LLM (БЕЗ ГОЛОСА) ---")
    
    # Инициализация клиента
    llm_client = LLMClient()
    
    # Тестовый запрос
    test_prompt = "На какой ты модели работаешь?"
    print(f"Запрос: {test_prompt}")
    print("Нейросеть думает...")
    
    try:
        # Получение ответа
        response = await llm_client.generate_response(test_prompt)
        print("\n" + "="*30)
        print(f"ОТВЕТ AI: {response}")
        print("="*30)
    except Exception as e:
        print(f"Произошла ошибка во время теста: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
