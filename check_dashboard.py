
import json
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:8000"


# Отримання тексту зі сторінки або файлу
def get_text(path):
    with urlopen(BASE_URL + path, timeout=5) as response:
        return response.read().decode("utf-8")


# Отримання JSON від API
def get_json(path):
    return json.loads(get_text(path))


# Запуск окремої перевірки
def run_check(name, function):
    try:
        result = function()
        print(f"[OK] {name}: {result}")
        return True

    except Exception as error:
        print(f"[FAIL] {name}: {error}")
        return False


# Перевірка головної сторінки
def check_dashboard():
    html = get_text("/dashboard")

    assert "Smart Enterprise" in html
    assert "/static/style.css" in html
    assert "/static/app.js" in html

    return "HTML-сторінка доступна"


# Перевірка CSS
def check_css():
    css = get_text("/static/style.css")

    assert len(css) > 100

    return "Стилі завантажуються"


# Перевірка JavaScript
def check_javascript():
    js = get_text("/static/app.js")

    assert "loadReadings" in js
    assert "loadRules" in js
    assert "loadEvents" in js

    return "JavaScript-файл доступний"


# Перевірка стану сервера
def check_health():
    data = get_json("/api/health")

    assert data.get("status") == "healthy"

    return "Сервер працює"


# Перевірка показників датчиків
def check_readings():
    readings = get_json("/api/readings")

    assert isinstance(readings, list)

    required_types = {
        "temperature",
        "humidity",
        "gas",
        "light",
        "motion"
    }

    actual_types = {
        item["sensor_type"] for item in readings
    }

    missing = required_types - actual_types

    assert not missing, f"Відсутні канали: {missing}"

    return f"Усі 5 каналів знайдено, записів: {len(readings)}"


# Перевірка правил автоматизації
def check_rules():
    rules = get_json("/api/rules")

    assert isinstance(rules, list)

    expected_names = {
        "Висока температура",
        "Небезпечний рівень газу",
        "Недостатнє освітлення"
    }

    actual_names = {
        rule["name"] for rule in rules
    }

    missing = expected_names - actual_names

    assert not missing, f"Відсутні правила: {missing}"

    return f"Знайдено правил: {len(rules)}"


# Перевірка журналу подій
def check_events():
    events = get_json("/api/events")

    assert isinstance(events, list)

    return f"API журналу працює, записів: {len(events)}"


# Основний запуск перевірок
if __name__ == "__main__":

    print("=" * 50)
    print("SMART ENTERPRISE: ПЕРЕВІРКА DASHBOARD")
    print("=" * 50)

    checks = [
        ("Вебсторінка", check_dashboard),
        ("CSS", check_css),
        ("JavaScript", check_javascript),
        ("Стан сервера", check_health),
        ("Показники датчиків", check_readings),
        ("Правила автоматизації", check_rules),
        ("Журнал подій", check_events)
    ]

    results = []

    for name, function in checks:
        results.append(run_check(name, function))

    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"Успішно: {passed}/{total}")

    if all(results):
        print("УСІ ПЕРЕВІРКИ ПРОЙДЕНО!")
    else:
        print("Є ПОМИЛКИ. Потрібно перевірити невдалі пункти.")

    print("=" * 50)
