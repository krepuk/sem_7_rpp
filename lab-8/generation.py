import asyncio
import json
import random
from datetime import datetime
from typing import AsyncGenerator, List, Dict

# Настройки
FILENAME = 'transactions.json'
CATEGORIES = ['Продукты', 'Транспорт', 'Развлечения', 'Коммуналка', 'Переводы']

# 1. Асинхронный генератор транзакций (Producer)
async def transaction_stream(count: int) -> AsyncGenerator[Dict, None]:
    """Генерирует по одной транзакции."""
    for _ in range(count):
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "category": random.choice(CATEGORIES),
            "amount": round(random.uniform(100.0, 5000.0), 2)
        }
        # Имитация асинхронной работы
        await asyncio.sleep(0.001) 
        yield transaction

# 2. Асинхронный группировщик (Batcher)
async def batch_stream(stream: AsyncGenerator, batch_size: int) -> AsyncGenerator[List[Dict], None]:
    """Собирает транзакции в пакеты по batch_size."""
    batch = []
    async for item in stream:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

# 3. Асинхронный писатель (Consumer)
async def save_to_file(batches: AsyncGenerator):
    """Сохраняет пакеты в файл, формируя валидный JSON массив."""
    print(f"Начинаем запись в {FILENAME}...")
    
    # Открываем файл и пишем начало JSON массива
    with open(FILENAME, 'w', encoding='utf-8') as f:
        f.write('[\n')
        
        first_batch = True
        
        async for batch in batches:
            # Если это не первый пакет, добавляем запятую перед новой пачкой
            if not first_batch:
                f.write(',\n')
            
            # Преобразуем список словарей в строку JSON (без внешних скобок списка, чтобы слить их)
            # Мы вручную форматируем, чтобы это был единый список объектов
            json_str = json.dumps(batch, ensure_ascii=False, indent=4)
            # Убираем внешние скобки [ и ] от dumps, чтобы вставить внутрь нашего массива
            content = json_str[1:-1] 
            
            f.write(content)
            
            print(f"-> Сохранена пачка из {len(batch)} записей.")
            first_batch = False
            
            # Имитация задержки записи
            await asyncio.sleep(0.1)
        
        # Закрываем JSON массив
        f.write('\n]')
    
    print(f"Готово! Данные сохранены в {FILENAME}")

async def main():
    try:
        count_str = input("Введите количество транзакций для генерации (например, 25): ")
        count = int(count_str)
        
        # Создаем конвейер (pipeline)
        # 1. Поток данных
        stream = transaction_stream(count)
        # 2. Группировка по 10
        batches = batch_stream(stream, batch_size=10)
        # 3. Сохранение (запуск конвейера)
        await save_to_file(batches)
        
    except ValueError:
        print("Ошибка: введите целое число.")

if __name__ == "__main__":
    # Запуск asyncio
    asyncio.run(main())