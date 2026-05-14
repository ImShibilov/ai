print("ТЕСТ 1: Python работает")

import os
from dotenv import load_dotenv

print("ТЕСТ 2: Импорт библиотек OK")

load_dotenv()

token = os.getenv("TG_BOT_TOKEN")
print(f"ТЕСТ 3: Токен найден: {token is not None}")
if token:
    print(f"   Первые 20 символов: {token[:20]}...")

print("✅ Все базовые проверки пройдены!")