import sys
from flask import Flask, jsonify

app = Flask(__name__)

# Получаем порт из аргументов командной строки (по умолчанию 5001)
try:
    PORT = int(sys.argv[1])
except IndexError:
    PORT = 5001

INSTANCE_ID = f"Instance_on_Port_{PORT}"

@app.route('/health', methods=['GET'])
def health():
    """Возвращает информацию о состоянии инстанса (200 OK)"""
    return jsonify({"status": "healthy", "instance_id": INSTANCE_ID}), 200

@app.route('/process', methods=['GET'])
def process():
    """Обрабатывает запрос и возвращает ID инстанса"""
    print(f"[{INSTANCE_ID}] Processing request...")
    return jsonify({"message": "Request processed", "processed_by": INSTANCE_ID})

if __name__ == '__main__':
    print(f"Starting instance on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)