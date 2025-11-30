import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("1. Сохраняем данные (POST /set)...")
resp = requests.post(f"{BASE_URL}/set", json={"key": "student", "value": "Ivanov"})
print(resp.json())

print("\n2. Проверяем наличие (GET /exists/)...")
resp = requests.get(f"{BASE_URL}/exists/student")
print(resp.json())

print("\n3. Получаем данные (GET /get/)...")
resp = requests.get(f"{BASE_URL}/get/student")
print(resp.json())

print("\n4. Удаляем данные (DELETE /delete/)...")
resp = requests.delete(f"{BASE_URL}/delete/student")
print(resp.json())

print("\n5. Проверяем работу лимитера (пытаемся сделать 11 запросов set подряд)...")
for i in range(12):
    resp = requests.post(f"{BASE_URL}/set", json={"key": f"test{i}", "value": i})
    if resp.status_code == 429:
        print(f"Запрос {i+1}: ОШИБКА 429 (Too Many Requests) - Лимитер работает!")
        break
    else:
        print(f"Запрос {i+1}: OK")