import time
import threading
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# --- Конфигурация пула инстансов ---
# Список словарей: {'url': 'http://...', 'healthy': True/False}
instances = []
current_index = 0  # Для Round Robin
lock = threading.Lock() # Для потокобезопасности при изменении списка

# --- Фоновая задача: Health Check ---
def health_check_loop():
    """Проверяет состояние всех инстансов каждые 5 секунд"""
    global instances
    while True:
        with lock:
            print(f"\n[Health Check] Checking {len(instances)} instances...")
            for instance in instances:
                try:
                    # Пытаемся постучаться на /health инстанса
                    response = requests.get(f"{instance['url']}/health", timeout=2)
                    if response.status_code == 200:
                        instance['healthy'] = True
                    else:
                        instance['healthy'] = False
                except requests.RequestException:
                    instance['healthy'] = False
                
                status = "UP" if instance['healthy'] else "DOWN"
                print(f" -> {instance['url']}: {status}")
        
        time.sleep(5)

# Запускаем проверку здоровья в отдельном потоке
checker_thread = threading.Thread(target=health_check_loop, daemon=True)
checker_thread.start()

# --- Логика Round Robin ---
def get_next_instance():
    """Выбирает следующий доступный инстанс по Round Robin"""
    global current_index
    with lock:
        # Фильтруем только здоровые инстансы
        active_instances = [inst for inst in instances if inst['healthy']]
        
        if not active_instances:
            return None
        
        # Round Robin логика
        # Мы используем глобальный индекс, но применяем его к отфильтрованному списку
        # (Упрощенная реализация для задачи)
        current_index = (current_index + 1) % len(active_instances)
        return active_instances[current_index]

# --- Маршруты Flask ---

@app.route('/')
def index():
    """Раздел IV: Web UI для управления пулом"""
    return render_template('index.html', instances=instances)

@app.route('/add_instance', methods=['POST'])
def add_instance():
    """Добавляет новый инстанс"""
    ip = request.form.get('ip')
    port = request.form.get('port')
    
    if ip and port:
        full_url = f"http://{ip}:{port}"
        with lock:
            # Проверка на дубликаты
            if not any(inst['url'] == full_url for inst in instances):
                instances.append({'url': full_url, 'healthy': False}) # Сначала False, HealthCheck обновит
    return redirect(url_for('index'))

@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    """Удаляет инстанс по индексу"""
    try:
        idx = int(request.form.get('index'))
        with lock:
            if 0 <= idx < len(instances):
                instances.pop(idx)
    except (ValueError, IndexError):
        pass
    return redirect(url_for('index'))

@app.route('/process')
def proxy_process():
    """
    Перенаправляет запрос клиента на активный инстанс (Round Robin)
    """
    target = get_next_instance()
    
    if not target:
        return jsonify({"error": "No healthy instances available"}), 503
    
    try:
        # Проксируем запрос на выбранный инстанс
        resp = requests.get(f"{target['url']}/process")
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to connect to instance: {str(e)}"}), 502

if __name__ == '__main__':
    print("Starting Load Balancer on port 5000...")
    app.run(host='0.0.0.0', port=5000)