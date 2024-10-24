from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import logging
from dotenv import load_dotenv
import os
from app.db.database import get_db
import app.db.crud as crud
from air_quality import get_city_by_coords, get_air_pollution_data, get_air_pollution_forecast

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Логирование
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()

# Создание диспетчера
dp = Dispatcher(storage=storage)  # Передаем storage в диспетчер

# Хэндлер команды /start с параметрами
@dp.message(Command("start"))
async def start(message: Message):
    logging.info(f"Получена команда /start от {message.from_user.id}")
    logging.info(f"А что именно передалось {message.text}")
    
    # Проверяем, что текст команды содержит необходимые параметры
    if message.text and "lon" in message.text and "lat" in message.text:
        try:
            # Извлекаем координаты из сообщения
            lon = message.text.split("lon")[1].split("lat")[0].strip()
            lat = message.text.split("lat")[1].strip()

            lon = float(lon.replace("-", "."))  # Преобразуем строку в float
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

            await message.answer(f"Спасибо за подписку на рассылку!\nГород: {city}\nКоординаты: {lon}, {lat}")

        except ValueError as e:
            logging.error(f"Ошибка: {e}")
            await message.answer(f"Подписка уже существует. Ваши данные были обновлены.\nГород: {city}\nКоординаты: {lon}, {lat}")

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            await message.answer("Произошла ошибка при обработке координат. Пожалуйста, проверьте формат и попробуйте снова.")
    
    else:
        await message.answer("Пожалуйста, укажите координаты в формате: /start lon36.19lat51.73")

# Функция отправки уведомлений
# Обновленная функция отправки уведомлений
async def send_notifications():
    logging.info("Функция send_notifications запущена")
    while True:
        try:
            with get_db() as db:
                users = crud.get_all_subscriptions(db)
                logging.info(f"Получено {len(users)} подписчиков")
                for user in users:
                    user_id = user.telegram_id
                    city = user.city
                    lon = user.lon
                    lat = user.lat
                    previous_aqi = user.current_aqi  # Получаем предыдущий AQI

                    # Логируем получение текущего AQI
                    logging.info(f"Получаем текущие данные AQI для пользователя {user_id} ({city})")

                    # Получаем текущие данные о качестве воздуха
                    air_data = await get_air_pollution_data(lat, lon)
                    current_aqi = air_data['list'][0]['main']['aqi']
                    logging.info(f"Текущий AQI для {city}: {current_aqi}")

                    # Если AQI изменился, отправляем уведомление
                    if previous_aqi and current_aqi != previous_aqi:
                        if current_aqi > previous_aqi:
                            trend = "повышение"
                        else:
                            trend = "понижение"
                        logging.info(f"Отправка уведомления о {trend} AQI пользователю {user_id} ({city})")
                        await bot.send_message(user_id, f"Внимание! В городе {city} наблюдается {trend} загрязнения. Текущий AQI: {current_aqi}")

                        # Обновляем текущий AQI в базе данных
                        crud.update_user_aqi(db, user_id, current_aqi)

                    # Логируем получение прогноза загрязнения
                    logging.info(f"Получаем прогноз AQI для пользователя {user_id} ({city})")

                    # Получаем прогноз загрязнения на ближайшие 6 часов
                    forecast_data = await get_air_pollution_forecast(lat, lon)
                    forecast_aqi = [f['main']['aqi'] for f in forecast_data['list'][:6]]  # Прогноз на 6 часов
                    logging.info(f"Прогноз AQI на ближайшие 6 часов для {city}: {forecast_aqi}")

                    # Проверяем на значительное изменение AQI
                    start_hour = None
                    end_hour = None
                    for i, forecast in enumerate(forecast_aqi):
                        logging.info(f"Анализируем прогноз на {i + 1} час: текущий AQI = {current_aqi}, прогноз AQI = {forecast}")
                        
                        # Если AQI изменяется на 2 или больше пунктов
                        if abs(forecast - current_aqi) >= 2:
                            if start_hour is None:
                                start_hour = i + 1  # Начало изменения (через сколько часов)
                            end_hour = i + 1  # Конец изменения (последний час)

                    # Если нашли изменения AQI в прогнозе
                    if start_hour is not None and end_hour is not None:
                        if forecast_aqi[end_hour - 1] > current_aqi:
                            trend = "ухудшение"
                        else:
                            trend = "улучшение"
                        logging.info(f"Отправка уведомления о {trend} качества воздуха через {start_hour} часов до {end_hour} часа(ов) пользователю {user_id} ({city})")
                        await bot.send_message(user_id, f"Внимание! В городе {city} ожидается {trend} качества воздуха через {start_hour} час(ов) и оно продлится до {end_hour} часа(ов). Прогнозируемый AQI: {forecast_aqi[end_hour-1]}")

        except Exception as e:
            logging.error(f"Ошибка в функции отправки уведомлений: {e}")
        
        await asyncio.sleep(30 * 60)  # Ожидаем 30 минут перед следующей проверкой

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