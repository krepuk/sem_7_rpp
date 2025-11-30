import json
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# --- Конфигурация хранилища ---
DATA_FILE = 'data.json'
data = {}

# --- Настройка Flask-Limiter ---
# Раздел II.3.a: Общее ограничение 100 запросов в сутки для всех маршрутов
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"],
    storage_uri="memory://"  # Храним данные лимитов в оперативной памяти
)

# --- Функции для работы с файлом (Раздел II.1) ---

def load_data():
    """Загружает данные из файла при старте."""
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Данные загружены из {DATA_FILE}")
        except json.JSONDecodeError:
            print("Ошибка чтения JSON, создано пустое хранилище.")
            data = {}
    else:
        print("Файл данных не найден, создано новое хранилище.")
        data = {}

def save_data():
    """Сохраняет текущее состояние словаря в файл."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

# --- API Маршруты (Раздел II.2) ---

@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute") # Раздел II.3.b: Лимит для set
def set_value():
    """
    Сохранить ключ-значение.
    Ожидает JSON вида: {"key": "имя", "value": "значение"}
    """
    req_data = request.get_json()
    
    if not req_data or 'key' not in req_data or 'value' not in req_data:
        return jsonify({"error": "Необходимо передать 'key' и 'value'"}), 400
    
    key = req_data['key']
    value = req_data['value']
    
    data[key] = value
    save_data() # Сохраняем сразу после изменения
    
    return jsonify({"message": "Ключ сохранен", "key": key, "value": value}), 200

@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    """Получить значение по ключу."""
    if key in data:
        return jsonify({"key": key, "value": data[key]}), 200
    return jsonify({"error": "Ключ не найден"}), 404

@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute") # Раздел II.3.b: Лимит для delete
def delete_value(key):
    """Удалить ключ."""
    if key in data:
        del data[key]
        save_data() # Сохраняем сразу после изменения
        return jsonify({"message": f"Ключ '{key}' удален"}), 200
    return jsonify({"error": "Ключ не найден"}), 404

@app.route('/exists/<key>', methods=['GET'])
def exists_key(key):
    """Проверить наличие ключа."""
    exists = key in data
    return jsonify({"key": key, "exists": exists}), 200

# --- Обработчик ошибок лимитов ---
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Превышен лимит запросов", "description": str(e.description)}), 429

# --- Запуск приложения ---
if __name__ == '__main__':
    load_data() # Загрузка данных при старте (Раздел II.1.a)
    app.run(debug=True, port=5000)