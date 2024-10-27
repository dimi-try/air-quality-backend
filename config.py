import os
import logging
from dotenv import load_dotenv


load_dotenv()

# ================ LOGGING ================
logging.basicConfig(level=logging.INFO)

# ================ TOKENS ================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# ================= URLS =================
GEOCODING_URL = "https://ipinfo.io/{ip}/geo"
OPENWEATHER_GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
OPENWEATHER_CURRENT_STATUS_URL = "http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
OPENWEATHER_FORECAST_URL = "http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"

# =============== DATABASE ===============
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')

DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


