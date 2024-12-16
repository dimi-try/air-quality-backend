# crud.py 
from sqlalchemy.orm import Session
from app.db.models import User, Subscription, Location, MapCache
from sqlalchemy.exc import NoResultFound
from config import MAP_DATA_TTL
import datetime
from worker import force_update_database
import logging

# Создание или обновление подписки пользователя
def create_or_update_subscription(
    db: Session, tg_user: dict, coordinates: dict, city: str, current_aqi: int
) -> Subscription:
    # Получаем пользователя по telegram_id
    user = db.query(User).filter(User.id == tg_user.id).first()

    if not user:
        # Если пользователь не найден, создаем нового
        user = User(
            id=tg_user.id, 
            username=tg_user.username, 
            first_name=tg_user.first_name, 
            last_name=tg_user.last_name
        )
        db.add(user)  # Добавляем пользователя в сессию
        db.commit()  # Сохраняем изменения в базе данных
        db.refresh(user)  # Обновляем объект user с реальными данными из БД

    # Удаляем существующую подписку пользователя (если есть)
    subscription = db.query(Subscription).filter(Subscription.user_id == tg_user.id).first()
    if subscription:
        delete_subscription(db, tg_user.id)

    # Проверяем наличие локации с указанными данными (город, координаты)
    location = (
        db.query(Location)
        .filter(
            Location.city == city, 
            Location.longitude == coordinates['lon'], 
            Location.latitude == coordinates['lat'])
        .first()
    )

    if not location:
        # Если локации нет, создаем новую
        location = Location(
            city=city, 
            longitude=coordinates['lon'], 
            latitude=coordinates['lat'], 
            aqi=current_aqi,
            created_by="telegram_user"
        )
        db.add(location)  # Добавляем новую локацию
        db.commit()
        db.refresh(location)

    # Проверяем наличие подписки для текущего пользователя и локации
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id, 
            Subscription.location_id == location.id)
        .first()
    )

    if subscription:
        # Если подписка существует, обновляем значение AQI для локации
        subscription.location.aqi = current_aqi
        db.commit()
        db.refresh(subscription)
        return subscription

    # Создаем новую подписку, если её не было
    new_subscription = Subscription(
        user_id=user.id, 
        location_id=location.id
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription

# Получение всех пользователей
def get_all_users(db: Session) -> list[Subscription]:
    # Возвращаем список всех пользователей из таблицы User
    return db.query(User).all()

# Добавление локаций из CSV-файла
def add_locations_from_csv(db: Session, locations_data: list[list[str]]) -> int:
    count = 0  # Счетчик успешно добавленных локаций
    try:
        for data in locations_data[1:]:  # Пропускаем заголовок CSV
            city, longitude, latitude, radius = data
            # Проверяем, существует ли локация с таким городом
            location_exists = db.query(Location).filter(Location.city == city).first()
            if location_exists:
                logging.info(f"Город {city} уже существует в таблице Location")
                continue
            # Создаем новую локацию
            location = Location(
                city=city,
                longitude=float(longitude),
                latitude=float(latitude),
                radius=int(radius.rstrip('\r')),
                created_by="default"
            )
            db.add(location)  # Добавляем локацию
            count += 1
        db.commit()  # Сохраняем изменения
        return count
    except Exception as e:
        logging.error(f"Ошибка при добавлении данных в таблицу Location: {e}")
        return 0
    force_update_database()  # Принудительное обновление базы данных

# Обновление значения AQI для указанной локации
def update_location_aqi(db: Session, coordinates: dict, current_aqi: int) -> Subscription:
    # Получаем локацию по координатам
    location = (
        db.query(Location)
        .filter(
            Location.longitude == coordinates['lon'], 
            Location.latitude == coordinates['lat'])
        .first()
    )
    # Обновляем значение AQI
    location.aqi = current_aqi
    db.commit()
    db.refresh(location)
    return location

# Удаление подписки пользователя
def delete_subscription(db: Session, telegram_id: int) -> bool:
    # Получаем подписку пользователя по telegram_id
    subscription = db.query(Subscription).filter(Subscription.user_id == telegram_id).first()
    if not subscription:
        return False  # Подписка не найдена
    
    db.delete(subscription)  # Удаляем подписку
    db.commit()
    return True

# Получение подписки по telegram_id
def get_subscription_by_telegram_id(db: Session, telegram_id: int) -> User:
    # Получаем пользователя по telegram_id
    user = db.query(User).filter(User.id == telegram_id).first()    
    if not user:
        return None

    # Обновляем объект пользователя
    db.refresh(user)  
    return user

# Получение всех локаций
def get_all_locations(db: Session) -> list[Location]:
    # Возвращаем все записи из таблицы Location
    return db.query(Location).all()

# Обновление данных кэша карты
def update_map_cache(db: Session, location_info: dict, location: Location) -> Location:
    # Проверяем наличие записи в MapCache для указанной локации
    map_cache = db.query(MapCache).filter(MapCache.location_id == location.id).first()

    if not map_cache:
        # Если записи нет, создаем новую
        map_cache = MapCache(
            location_id=location.id,
            expiration_date=datetime.datetime.utcfromtimestamp(location_info['list'][0]['dt'] + MAP_DATA_TTL),
            co=location_info['list'][0]['components']['co'],
            no=location_info['list'][0]['components']['no'],
            no2=location_info['list'][0]['components']['no2'],
            o3=location_info['list'][0]['components']['o3'],
            so2=location_info['list'][0]['components']['so2'],
            pm2_5=location_info['list'][0]['components']['pm2_5'],
            pm10=location_info['list'][0]['components']['pm10'],
            nh3=location_info['list'][0]['components']['nh3']
        )
        db.add(map_cache)  # Добавляем запись в кэш
        db.commit()
        db.refresh(map_cache)
        return location

    # Обновляем данные в существующей записи MapCache
    map_cache.expiration_date = datetime.datetime.utcfromtimestamp(location_info['list'][0]['dt'] + MAP_DATA_TTL)
    map_cache.co =              location_info['list'][0]['components']['co']
    map_cache.no =              location_info['list'][0]['components']['no']
    map_cache.no2 =             location_info['list'][0]['components']['no2']
    map_cache.o3 =              location_info['list'][0]['components']['o3']
    map_cache.so2 =             location_info['list'][0]['components']['so2']
    map_cache.pm2_5 =           location_info['list'][0]['components']['pm2_5']
    map_cache.pm10 =            location_info['list'][0]['components']['pm10']
    map_cache.nh3 =             location_info['list'][0]['components']['nh3']

    db.commit()
    db.refresh(location)
    return location

# Получение данных кэша карты
def get_map_cache(db: Session) -> list[Location]:
    # Возвращаем все записи из таблицы MapCache
    return db.query(MapCache).all()
