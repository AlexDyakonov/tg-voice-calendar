import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Yandex SpeechKit настройки
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')

# Проверяем наличие обязательных переменных
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

if not YANDEX_API_KEY:
    raise ValueError("YANDEX_API_KEY не установлен в переменных окружения")

if not YANDEX_FOLDER_ID:
    raise ValueError("YANDEX_FOLDER_ID не установлен в переменных окружения") 