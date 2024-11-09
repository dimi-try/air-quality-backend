import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.db.database import get_db
import app.db.crud as crud
import app.bot.messages as messages
from app.bot.utils import get_coordinates
from air_quality import get_city_by_coords, get_air_pollution_data, get_air_pollution_forecast
from config import TELEGRAM_BOT_TOKEN, AIR_QUALITY_CHECK_INTERVAL
from datetime import datetime, time, timedelta

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хэндлер команды /start с кнопками
@dp.message(Command("start"))
async def start(message: Message):
    logging.info(f"[TELEGRAM BOT] /start от {message.from_user.id} message: {message.text}")
    coordinates = get_coordinates(message)

    # Создаем кнопки для клавиатуры
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Проверить качество воздуха")],
            [KeyboardButton(text="Отписаться от уведомлений")]
        ],
        resize_keyboard=True
    )

    if coordinates:
        try:            
            city = await get_city_by_coords(coordinates["lat"], coordinates["lon"])
            air_data = await get_air_pollution_data(coordinates["lat"], coordinates["lon"])
            current_aqi = air_data['list'][0]['main']['aqi']

            with get_db() as db:
                telegram_id = message.from_user.id
                crud.create_or_update_subscription(
                    db,
                    telegram_id=telegram_id,
                    city=city,
                    lon=coordinates['lon'],
                    lat=coordinates['lat'],
                    current_aqi=current_aqi
                )

            await message.answer(
                messages.MESSAGE_SAVE_SUBSCRIPTION + f"{city}",
                reply_markup=keyboard  # Отправляем сообщение с клавиатурой
            )

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            await message.answer(messages.MESSAGE_START_ERROR)

    else:
        await message.answer(messages.MESSAGE_COORDINATES_NOT_PROVIDED, reply_markup=keyboard)

# Хэндлер для обработки текстовых сообщений с кнопок
@dp.message(lambda message: message.text == "Проверить качество воздуха")
async def check_air_quality(message: Message):
    # Реализация проверки качества воздуха
    try:
        # Получаем данные пользователя из базы
        with get_db() as db:
            user_data = crud.get_subscription_by_telegram_id(db, telegram_id=message.from_user.id)
            # Проверяем, удалось ли получить данные пользователя из базы
            if user_data and user_data.lat is not None and user_data.lon is not None:
                # Используем координаты из базы
                air_data = await get_air_pollution_data(user_data.lat, user_data.lon)
                current_aqi = air_data['list'][0]['main']['aqi']
                await message.answer(f"Текущий AQI для {user_data.city}: {current_aqi}")
            else:
                await message.answer(messages.MESSAGE_COORDINATES_NOT_PROVIDED)
    
    except Exception as e:
        logging.error(f"Ошибка при проверке качества воздуха: {e}")
        await message.answer("Произошла ошибка при проверке качества воздуха.")

@dp.message(lambda message: message.text == "Отписаться от уведомлений")
async def unsubscribe(message: Message):
    # Обработка отписки
    with get_db() as db:
        success = crud.delete_subscription(db, telegram_id=message.from_user.id)
        if success:
            await message.answer(messages.USER_UNSUBSCRIBED)
        else:
            await message.answer(messages.USER_UNSUBSCRIBED_ERROR)

# Функция отправки уведомлений
async def send_notifications():
    logging.info("Функция send_notifications запущена")
    while True:
        now = datetime.now()
        next_8am = datetime.combine(now.date(), time(8)) + timedelta(days=(now.hour >= 8))
        next_8pm = datetime.combine(now.date(), time(20)) + timedelta(days=(now.hour >= 20))
        next_regular_notification_time = min(next_8am, next_8pm)

        try:
            with get_db() as db:
                users = crud.get_all_subscriptions(db)
                for user in users:
                    previous_aqi = user.current_aqi
                    air_data = await get_air_pollution_data(user.lat, user.lon)
                    current_aqi = air_data['list'][0]['main']['aqi']
                    
                    # Экстренное уведомление при значительном изменении AQI
                    if previous_aqi and current_aqi != previous_aqi:
                        trend = "повышение" if current_aqi > previous_aqi else "понижение"
                        crud.update_user_aqi(db, user.telegram_id, current_aqi)
                        await bot.send_message(user.telegram_id, f"Внимание! В городе {user.city} наблюдается {trend} загрязнения. Текущий AQI: {current_aqi}")

                    # Прогноз на ближайшие 6 часов для экстренных уведомлений
                    forecast_data = await get_air_pollution_forecast(user.lat, user.lon)
                    forecast_aqi = [f['main']['aqi'] for f in forecast_data['list'][:6]]
                    for i, forecast in enumerate(forecast_aqi):
                        if abs(forecast - current_aqi) >= 2:
                            trend = "ухудшение" if forecast > current_aqi else "улучшение"
                            hours = (i + 1) * 1
                            await bot.send_message(user.telegram_id, f"Внимание! Через {hours} часов ожидается {trend} качества воздуха в городе {user.city}. Прогнозируемый AQI: {forecast}")
                            break

                    # Регулярное уведомление (в 8:00 и 20:00)
                    if now >= next_regular_notification_time:
                        trend = "ухудшение" if current_aqi >= 3 else "нормальный уровень"
                        await bot.send_message(user.telegram_id, f"Ежедневный отчет: качество воздуха в {user.city} {trend}. Текущий AQI: {current_aqi}")
                        next_regular_notification_time += timedelta(hours=12)  # Следующее уведомление через 12 часов

        except Exception as e:
            logging.error(f"Ошибка в функции отправки уведомлений: {e}")
        
        await asyncio.sleep(AIR_QUALITY_CHECK_INTERVAL)

# Запуск бота
async def start_bot():
    logging.info("Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Передаем bot в start_polling

