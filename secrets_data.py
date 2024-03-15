import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()


BOT_TOKEN = os.getenv("DTP_BOT_TOKEN")
MAP_API = os.getenv("MAP_API")