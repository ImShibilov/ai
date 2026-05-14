import asyncio
import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv  # Импортируем загрузчик env

# --- ЗАГРУЗКА ПЕРЕМЕННЫХ ИЗ .env ---
load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

# Проверка, загрузились ли токены
if not all([TG_BOT_TOKEN, GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET]):
    raise ValueError("❌ Ошибка: Не все переменные найдены в файле .env. Проверьте названия ключей.")

# URL API Сбера
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

# Логирование
logging.basicConfig(level=logging.INFO)

# Запуск бота
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

def get_token():
    """Получает токен доступа"""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '12345678-1234-1234-1234-123456789012' 
    }
    payload = {
        'scope': 'GIGACHAT_API_PERS',
        'client_id': GIGACHAT_CLIENT_ID,
        'client_secret': GIGACHAT_CLIENT_SECRET
    }
    try:
        response = requests.post(AUTH_URL, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Ошибка получения токена: {e}")
        return None

def ask_gigachat(text):
    """Отправляет запрос в GigaChat"""
    token = get_token()
    if not token:
        return "Ошибка авторизации в Sber GigaChat."

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    body = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": text}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(CHAT_URL, headers=headers, json=body, verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return "Ошибка при обращении к нейросети."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот на GigaChat. Спроси меня о чем-нибудь.")

@dp.message()
async def echo_message(message: types.Message):
    wait_msg = await message.answer("Думаю...")
    answer = ask_gigachat(message.text)
    await wait_msg.edit_text(answer)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())