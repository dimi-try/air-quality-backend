import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message
from app.db.database import get_db
import app.db.crud as crud
import app.bot.messages as messages
from air_quality import get_city_by_coords, get_air_pollution_data, get_air_pollution_forecast
from config import TELEGRAM_BOT_TOKEN

# Логирование

# Создание экземпляра бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()

# Создание диспетчера
dp = Dispatcher(storage=storage)  # Передаем storage в диспетчер

# Хэндлер команды /start с параметрами
@dp.message(Command("start"))
async def start(message: Message):
    logging.info(f"[TELEGRAM BOT] /start от {message.from_user.id} message: {message.text}")
    
    # Проверяем, что текст команды содержит необходимые параметры
    if message.text and "lon" in message.text and "lat" in message.text:
        try:
            # Извлекаем координаты из сообщения
            lon = message.text.split("lon")[1].split("lat")[0].strip()
            lat = message.text.split("lat")[1].strip()

            lon = float(lon.replace("-", "."))
            lat = float(lat.replace("-", "."))

            # Вместо геокодера по умолчанию город Астрахань - исправлено
            city = await get_city_by_coords(lat, lon)

            # Получаем текущие данные о качестве воздуха
            air_data = await get_air_pollution_data(lat, lon)
            current_aqi = air_data['list'][0]['main']['aqi']
            
            with get_db() as db:
                telegram_id = message.from_user.id
                # Используем функцию create_or_update_subscription
                crud.create_or_update_subscription(
                    db,
                    telegram_id=telegram_id,
                    city=city,
                    lon=lon,
                    lat=lat,
                    current_aqi=current_aqi
                    
                )

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
            # Логика пробежки по базе данных и проверки условий загрязнения
            with get_db() as db:
                users = crud.get_all_subscriptions(db)  # Получаем всех подписчиков
                logging.info(f"Получено {len(users)} подписчиков")
                for user in users:
                    user_id = user.telegram_id
                    city = user.city
                    lon = user.lon
                    lat = user.lat
                    previous_aqi = user.current_aqi  # Получаем предыдущий AQI

                    # Получаем текущие данные о качестве воздуха
                    air_data = await get_air_pollution_data(lat, lon)
                    current_aqi = air_data['list'][0]['main']['aqi']

                    # Если AQI изменился, отправляем уведомление
                    if previous_aqi and current_aqi != previous_aqi:
                        if current_aqi > previous_aqi:
                            trend = "повышение"
                        else:
                            trend = "понижение"
                        await bot.send_message(user_id, f"Внимание! В городе {city} наблюдается {trend} загрязнения. Текущий AQI: {current_aqi}")

                        # Обновляем текущий AQI в базе данных
                        crud.update_user_aqi(db, user_id, current_aqi)

                    # Получаем прогноз загрязнения на ближайшие 6 часов
                    forecast_data = await get_air_pollution_forecast(lat, lon)
                    forecast_aqi = [f['main']['aqi'] for f in forecast_data['list'][:6]]  # Прогноз на 6 часов

                    # Проверяем на значительное изменение AQI
                    for i, forecast in enumerate(forecast_aqi):
                        if abs(forecast - current_aqi) >= 2:  # Изменение на 2 или более пунктов
                            if forecast > current_aqi:
                                trend = "ухудшение"
                            else:
                                trend = "улучшение"
                            hours = (i + 1) * 1  # Час прогноза (от 1 до 6)
                            await bot.send_message(user_id, f"Внимание! Через {hours} часов ожидается {trend} качества воздуха в городе {city}. Прогнозируемый AQI: {forecast}")
                            break
                        
        except Exception as e:
            logging.error(f"Ошибка в функции отправки уведомлений: {e}")
        await asyncio.sleep(3)  # Ожидаем 30 минут перед следующей проверкой


# Хэндлер команды /stop
@dp.message(Command("stop"))
async def stop(message: Message):
    with get_db() as db:
        success = crud.delete_subscription(db, telegram_id=message.from_user.id)
        if success:
            await message.answer("Вы отписались от уведомлений.")
        else:
            await message.answer("Вы не были подписаны на уведомления.")

# Запуск бота
async def start_bot():
    logging.info("Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Передаем bot в start_polling