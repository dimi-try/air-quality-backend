import os
import logging
from dotenv import load_dotenv


load_dotenv()

# ================ LOGGING ================
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ================ TOKENS ================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# ================= URLS =================
GEOCODING_URL = "https://ipinfo.io/{ip}/geo"

OPENWEATHER_URL = "http://api.openweathermap.org"
OPENWEATHER_GEOCODING_URL =       OPENWEATHER_URL + "/geo/1.0/reverse?lat={lat}&lon={lon}"                  + f"&appid={OPENWEATHER_API_KEY}"
OPENWEATHER_CURRENT_STATUS_URL =  OPENWEATHER_URL + "/data/2.5/air_pollution?lat={lat}&lon={lon}"           + f"&appid={OPENWEATHER_API_KEY}"
OPENWEATHER_FORECAST_URL =        OPENWEATHER_URL + "/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}"  + f"&appid={OPENWEATHER_API_KEY}"

# тестируем текущее состояние воздуха с помощью тестовых данных
# OPENWEATHER_CURRENT_STATUS_URL = "http://localhost:80/api/air"

# =============== DATABASE ===============
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')

DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# =============== OTHER ================
AIR_QUALITY_CHECK_INTERVAL = 60 # Переменная указывающая периодичность проверки в секундах


