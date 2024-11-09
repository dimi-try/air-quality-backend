# crud.py
from sqlalchemy.orm import Session
from app.db.models import Subscription

# Create or Update
def create_or_update_subscription(db: Session, telegram_id: int, city: str, lon: float, lat: float, current_aqi: int) -> Subscription:
    # Проверяем, существует ли уже запись с таким telegram_id
    existing_subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()
    
    if existing_subscription:
        # Обновляем существующую запись
        existing_subscription.city = city
        existing_subscription.lon = lon
        existing_subscription.lat = lat
        existing_subscription.current_aqi = current_aqi
        db.commit()
        db.refresh(existing_subscription)
        return existing_subscription
    
    # Если подписки нет, создаем новую
    new_subscription = Subscription(telegram_id=telegram_id, city=city, lon=lon, lat=lat, current_aqi=current_aqi)
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

# Добавляем функцию для получения всех 
def get_all_subscriptions(db: Session) -> list[Subscription]:
    return db.query(Subscription).all()

# Update aqi
def update_user_aqi(db: Session, telegram_id: int, current_aqi: int) -> Subscription:
    subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()
    if not subscription:
        return None
    subscription.current_aqi = current_aqi
    db.commit()
    db.refresh(subscription)
    return subscription

# Delete
def delete_subscription(db: Session, telegram_id: int) -> bool:
    subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()
    if not subscription:
        return False
    db.delete(subscription)
    db.commit()
    return True


# Получение подписки по telegram_id
def get_subscription_by_telegram_id(db: Session, telegram_id: int) -> Subscription:
    subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()    
    if not subscription:
        return None

    # Обновляем объект, чтобы он снова был привязан к сессии
    db.refresh(subscription)  # Это позволяет убедиться, что атрибуты объекта доступны

    return subscription