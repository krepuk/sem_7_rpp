import asyncio
import json
import os
from typing import List, Dict

FILENAME = 'transactions.json'

# Условные лимиты трат (для пункта II.c)
LIMITS = {
    'Продукты': 15000,
    'Транспорт': 5000,
    'Развлечения': 3000,
    'Коммуналка': 10000,
    'Переводы': 10000
}

async def load_transactions() -> List[Dict]:
    """Асинхронная (имитация) загрузка данных из файла."""
    if not os.path.exists(FILENAME):
        print("Файл не найден! Сначала запустите generator.py")
        return []
    
    print(f"Чтение файла {FILENAME}...")
    # В реальных высоконагруженных системах используют aiofiles, 
    # но стандартный json.load блокирующий. Для лабы обернем в to_thread (Python 3.9+) 
    # или просто выполним синхронно, так как библиотека стандартная.
    # Здесь сделаем вид, что чтение идет потоком.
    await asyncio.sleep(0.5) 
    
    with open(FILENAME, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

async def process_data(data: List[Dict]):
    """Реактивная обработка списка транзакций."""
    results = {}
    
    # Эмуляция потоковой обработки списка
    for tx in data:
        cat = tx['category']
        amt = tx['amount']
        
        if cat not in results:
            results[cat] = 0.0
        
        results[cat] += amt
        # Можно добавить await asyncio.sleep(0), чтобы не блокировать цикл при огромном списке
    
    return results

async def check_limits(results: Dict[str, float]):
    """Вывод итогов и проверка превышений."""
    print("\n--- Результаты анализа ---")
    for category, total in results.items():
        limit = LIMITS.get(category, 0)
        formatted_total = f"{total:,.2f}"
        
        print(f"Категория: {category:<15} | Сумма: {formatted_total}")
        
        if total > limit:
            diff = total - limit
            print(f"   [!] ВНИМАНИЕ: Превышение лимита ({limit}) на {diff:,.2f}!")

async def main():
    # 1. Загрузка
    transactions = await load_transactions()
    
    if transactions:
        print(f"Загружено {len(transactions)} транзакций.")
        
        # 2. Группировка и суммирование
        category_totals = await process_data(transactions)
        
        # 3. Вывод результатов и превышений
        await check_limits(category_totals)

if __name__ == "__main__":
    asyncio.run(main())
