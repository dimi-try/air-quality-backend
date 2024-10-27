import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message
from app.db.database import get_db
import app.db.crud as crud
import app.bot.messages as messages
from app.bot.utils import get_coordinates
from app.bot.db_interface import create_or_update_subscription
from air_quality import get_city_by_coords, get_air_pollution_data, get_air_pollution_forecast
from config import TELEGRAM_BOT_TOKEN, AIR_QUALITY_CHECK_INTERVAL


bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(storage=storage)

# Хэндлер команды /start с параметрами
@dp.message(Command("start"))
async def start(message: Message):
    logging.info(f"[TELEGRAM BOT] /start от {message.from_user.id} message: {message.text}")

    coordinates = get_coordinates(message)
    
    # Проверяем, что текст команды содержит необходимые параметры
    if coordinates:
        try:            
            # Вместо геокодера по умолчанию город Астрахань - исправлено
            city = await get_city_by_coords(coordinates["lat"], coordinates["lon"])

            # Получаем текущие данные о качестве воздуха
            air_data = await get_air_pollution_data(coordinates["lat"], coordinates["lon"])
            current_aqi = air_data['list'][0]['main']['aqi']
            
            create_or_update_subscription(message, city, coordinates, current_aqi)

            await message.answer(messages.MESSAGE_SAVE_SUBSCRIPTION + f"{city}")

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            await message.answer(messages.MESSAGE_START_ERROR)
    
    else:
        await message.answer(messages.MESSAGE_COORDINATES_NOT_PROVIDED)

# Функция отправки уведомлений
async def send_notifications():
    logging.info("Функция send_notifications запущена")
    while True:
        try:
            with get_db() as db:
                users = crud.get_all_subscriptions(db)
                # logging.info(f"Получено {len(users)} подписчиков")
                for user in users:
                    previous_aqi = user.current_aqi  # Получаем предыдущий AQI

                    # Получаем текущие данные о качестве воздуха
                    air_data = await get_air_pollution_data(user.lat, user.lon)
                    current_aqi = air_data['list'][0]['main']['aqi']

                    # Если AQI изменился, отправляем уведомление
                    if previous_aqi and current_aqi != previous_aqi:
                        trend = "повышение" if current_aqi > previous_aqi else "понижение"
                        
                        # Обновляем текущий AQI в базе данных
                        crud.update_user_aqi(db, user.telegram_id, current_aqi)
                        
                        await bot.send_message(user.telegram_id, f"Внимание! В городе {user.city} наблюдается {trend} загрязнения. Текущий AQI: {current_aqi}")

                    # Получаем прогноз загрязнения на ближайшие 6 часов
                    forecast_data = await get_air_pollution_forecast(user.lat, user.lon)
                    forecast_aqi = [f['main']['aqi'] for f in forecast_data['list'][:6]]  # Прогноз на 6 часов

                    # Проверяем на значительное изменение AQI
                    for i, forecast in enumerate(forecast_aqi):
                        if abs(forecast - current_aqi) >= 1:  # Изменение на 2 или более пунктов
                            trend = "ухудшение" if forecast > current_aqi else "улучшение"
                            hours = (i + 1) * 1  # Час прогноза (от 1 до 6)
                            await bot.send_message(user.telegram_id, f"Внимание! Через {hours} часов ожидается {trend} качества воздуха в городе {user.city}. Прогнозируемый AQI: {forecast}")
                            break
                        
        except Exception as e:
            logging.error(f"Ошибка в функции отправки уведомлений: {e}")
        await asyncio.sleep(AIR_QUALITY_CHECK_INTERVAL)


# Хэндлер команды /stop
@dp.message(Command("stop"))
async def stop(message: Message):
    with get_db() as db:
        success = crud.delete_subscription(db, telegram_id=message.from_user.id)
        if success:
            await message.answer(USER_UNSUBSCRIBED)
        else:
            await message.answer(USER_UNSUBSCRIBED_ERROR)

# Запуск бота
async def start_bot():
    logging.info("Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Передаем bot в start_polling