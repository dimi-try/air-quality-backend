import asyncio
import logging
import aiohttp
from worker import force_update_database
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.db.database import get_db
import app.db.crud as crud
import app.bot.messages as messages
from app.bot.utils import get_coordinates
from app.bot.aqi_utils import get_aqi_info, format_aqi_message
from air_quality import get_city_by_coords, get_air_pollution_data, get_air_pollution_forecast
from config import TELEGRAM_BOT_TOKEN, AIR_QUALITY_CHECK_INTERVAL, TG_ADMIN_IDs
from datetime import datetime, time, timedelta

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Создаем кнопки для клавиатуры
keyboard = ReplyKeyboardMarkup(
  keyboard=[
    [KeyboardButton(text="Проверить качество воздуха")],
    [KeyboardButton(text="Отписаться от уведомлений")]
  ],
  resize_keyboard=True
)

# Клавиатура админа
admin_keyboard = ReplyKeyboardMarkup(
  keyboard=[
    [KeyboardButton(text="Обновить все данные карты")],
  ],
  resize_keyboard=True
)

# Хэндлер команды /start с кнопками
@dp.message(Command("start"))
async def start(message: Message):
  logging.info(f"[TELEGRAM BOT] /start от {message.from_user.id} message: {message.text}")
  coordinates = get_coordinates(message)
  print("coordinates: ", coordinates)

  if coordinates:
    try:            
      city = await get_city_by_coords(coordinates["lat"], coordinates["lon"])
      air_data = await get_air_pollution_data(coordinates["lat"], coordinates["lon"])
      current_aqi = air_data['list'][0]['main']['aqi']

      with get_db() as db:
        crud.create_or_update_subscription(
          db,
          tg_user=message.from_user,
          coordinates=coordinates,
          city=city,
          current_aqi=current_aqi
        )

        await message.answer(
          messages.MESSAGE_SAVE_SUBSCRIPTION + f"{city}",
          reply_markup=keyboard
        )

    except Exception as e:
      logging.error(f"Произошла ошибка: {e}")
      await message.answer(messages.MESSAGE_START_ERROR)

  else:
    await message.answer(messages.MESSAGE_COORDINATES_NOT_PROVIDED, reply_markup=keyboard)

# Хэндлер команды /admin с кнопками
@dp.message(Command("admin"))
async def start(message: Message):
  if message.from_user.id not in TG_ADMIN_IDs:
    await message.answer("Вы не имеете доступа к этой функции")
    return

  logging.info(f"[TELEGRAM BOT] /admin от {message.from_user.id}")
  await message.answer("Добро пожаловать в админ-панель!", reply_markup=admin_keyboard)

# Хэндлер для обработки текстовых сообщений с кнопок
@dp.message(lambda message: message.text == "Проверить качество воздуха")
async def check_air_quality(message: Message):
  try:
    # Получаем данные пользователя из базы
    with get_db() as db:
      user = crud.get_subscription_by_telegram_id(db, telegram_id=message.from_user.id)
      # Проверяем, удалось ли получить данные пользователя из базы
      if user:
        location = user.subscription.location
        air_data = await get_air_pollution_data(location.latitude, location.longitude)
        current_aqi = air_data['list'][0]['main']['aqi']
        aqi_info = get_aqi_info(current_aqi)
        await message.answer(
          f"Текущий AQI для {location.city}: {current_aqi} {aqi_info['emoji']} ({aqi_info['description']})",
          reply_markup=keyboard
        )
      else:
        await message.answer(messages.MESSAGE_COORDINATES_NOT_PROVIDED, reply_markup=keyboard)
  
  except Exception as e:
    logging.error(f"Ошибка при проверке качества воздуха: {e}")
    await message.answer("Произошла ошибка при проверке качества воздуха.", reply_markup=keyboard)

@dp.message(lambda message: message.text == "Отписаться от уведомлений")
async def unsubscribe(message: Message):
  # Обработка отписки
  with get_db() as db:
    success = crud.delete_subscription(db, telegram_id=message.from_user.id)
    if success:
      await message.answer(messages.USER_UNSUBSCRIBED)
    else:
      await message.answer(messages.USER_UNSUBSCRIBED_ERROR)

# Хэндлер для обработки геопозиций
@dp.message(lambda message: message.location is not None)
async def handle_location(message: Message):
  # Получаем координаты
  latitude = message.location.latitude
  longitude = message.location.longitude
  logging.info(f"[TELEGRAM BOT] Получена геопозиция от пользователя {message.from_user.id}: "
                f"Широта: {latitude}, Долгота: {longitude}")
  
  # Сохраняем данные в базе
  city = await get_city_by_coords(latitude, longitude)
  coordinates = {"lat": latitude, "lon": longitude}
  air_data = await get_air_pollution_data(latitude, longitude)
  current_aqi = air_data['list'][0]['main']['aqi']
  aqi_info = get_aqi_info(current_aqi)
  with get_db() as db:
    telegram_id = message.from_user.id
    crud.create_or_update_subscription(
      db,
      tg_user=message.from_user,
      coordinates=coordinates,
      city=city,
      current_aqi=current_aqi
    )
  # Ответ на сообщение с геопозицией
  await message.answer(
    f"♥️ Спасибо, ваша подписка сохранена!\n📍 Местоположение: {city}\n🏭 Текущий AQI: {current_aqi} {aqi_info['emoji']} ({aqi_info['description']})",
    reply_markup=keyboard
  )

# Функция отправки уведомлений
async def send_notifications():
  while True:
    now = datetime.now()
    next_8am = datetime.combine(now.date(), time(8)) + timedelta(days=(now.hour >= 8))
    next_8pm = datetime.combine(now.date(), time(20)) + timedelta(days=(now.hour >= 20))
    next_regular_notification_time = min(next_8am, next_8pm)

    try:
      with get_db() as db:
        users = crud.get_all_users(db)
        for user in users:
          previous_aqi = user.subscription.location.aqi
          user_city = user.subscription.location.city
          coordinates = {'lon': user.subscription.location.longitude, 'lat': user.subscription.location.latitude}

          air_data = await get_air_pollution_data(coordinates['lat'], coordinates['lon'])
          current_aqi = air_data['list'][0]['main']['aqi']
          aqi_info = get_aqi_info(current_aqi)
                    
          # Экстренное уведомление при значительном изменении AQI
          if previous_aqi and current_aqi != previous_aqi:
            trend = "ухудшение 😷☁️" if current_aqi > previous_aqi else "улучшение ☺️☀️"
            crud.update_location_aqi(db, coordinates, current_aqi)
            await bot.send_message(
              user.id, 
              f"В вашем городе {user_city} наблюдается {trend} качества воздуха.\n🏭 Текущий AQI: {current_aqi} {aqi_info['emoji']} ({aqi_info['description']})"
              )

          # Прогноз на ближайшие 6 часов для экстренных уведомлений
          forecast_data = await get_air_pollution_forecast(coordinates['lat'], coordinates['lon'])
          forecast_aqi = [f['main']['aqi'] for f in forecast_data['list'][:6]]
          for i, forecast in enumerate(forecast_aqi):
            if abs(forecast - current_aqi) >= 2:
              trend = "ухудшение 😷☁️" if forecast > current_aqi else "улучшение ☺️☀️"
              hours = (i + 1) * 1
              forecast_info = get_aqi_info(forecast)
              await bot.send_message(user.id, 
              f"Внимание! Через {hours} часов ожидается значительное {trend} качества воздуха в городе {user_city}.\n🏭 Текущий AQI: {current_aqi} {aqi_info['emoji']} ({aqi_info['description']}) Прогнозируемый AQI: {forecast} {forecast_info['emoji']} ({forecast_info['description']})")
              break

          # Регулярное уведомление (в 8:00 и 20:00)
          if now >= next_regular_notification_time:
            trend = "ухудшение" if current_aqi >= 3 else "нормальный уровень"
            await bot.send_message(
              user.id,
              f"Ежедневный отчет: качество воздуха в {user_city} {trend}. Текущий AQI: {current_aqi} {aqi_info['emoji']} ({aqi_info['description']})"
            )
            next_regular_notification_time += timedelta(hours=12)  # Следующее уведомление через 12 часов

    except Exception as e:
      logging.error(f"Ошибка в функции отправки уведомлений: {e}")
    
    await asyncio.sleep(AIR_QUALITY_CHECK_INTERVAL)

# Хэндлер для обработки файлов
@dp.message(lambda message: message.document is not None)
async def handle_csv_file(message: Message):
  if message.from_user.id not in TG_ADMIN_IDs:
    await message.answer("Вы не имеете доступа к этой функции")
    return
  
  # Обработка файла
  file_id = message.document.file_id
  file_info = await bot.get_file(file_id)
  file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
  # try:
  async with aiohttp.ClientSession() as session:
    async with session.get(file_url) as response:
      file_data = await response.text()
      csv_data = [line.split(',') for line in file_data.strip().split('\n')]
      with get_db() as db:
        locationsAdded = crud.add_locations_from_csv(db, csv_data)
        await message.answer(f"Успешно! Было добавлено {locationsAdded} мест.")
      

# Запуск бота
async def start_bot():
  logging.info("Запуск бота...")
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


