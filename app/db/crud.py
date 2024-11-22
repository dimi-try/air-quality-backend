# crud.py
from sqlalchemy.orm import Session
from app.db.models import User, Subscription, Location
from sqlalchemy.exc import NoResultFound


def create_or_update_subscription(
    db: Session, tg_user: dict, coordinates: dict, city: str, current_aqi: int
) -> Subscription:
    # Проверяем, существует ли пользователь с указанным telegram_id
    user = db.query(User).filter(User.id == tg_user.id).first()

    if not user:
        # Если пользователя нет, создаем его
        user = User(
            id=tg_user.id, 
            username=tg_user.username, 
            first_name=tg_user.first_name, 
            last_name=tg_user.last_name
            )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Проверяем, существует ли локация с указанными данными
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
            aqi=current_aqi)
        db.add(location)
        db.commit()
        db.refresh(location)

    # Проверяем, существует ли подписка для данного пользователя и локации
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id, 
            Subscription.location_id == location.id)
        .first()
    )

    if subscription:
        # Если подписка существует, обновляем её
        subscription.location.aqi = current_aqi  # Обновляем AQI локации
        db.commit()
        db.refresh(subscription)
        return subscription

    # Если подписки нет, создаем новую
    new_subscription = Subscription(
        user_id=user.id, 
        location_id=location.id
        )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription


# Добавляем функцию для получения всех 
# def get_all_subscriptions(db: Session) -> list[Subscription]:
#     return db.query(Subscription).all()

# # Update aqi
# def update_user_aqi(db: Session, telegram_id: int, current_aqi: int) -> Subscription:
#     subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()
#     if not subscription:
#         return None
#     subscription.current_aqi = current_aqi
#     db.commit()
#     db.refresh(subscription)
#     return subscription

# # Delete
# def delete_subscription(db: Session, telegram_id: int) -> bool:
#     subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()
#     if not subscription:
#         return False
#     db.delete(subscription)
#     db.commit()
#     return True


# # Получение подписки по telegram_id
# def get_subscription_by_telegram_id(db: Session, telegram_id: int) -> Subscription:
#     subscription = db.query(Subscription).filter(Subscription.telegram_id == telegram_id).first()    
#     if not subscription:
#         return None

#     # Обновляем объект, чтобы он снова был привязан к сессии
#     db.refresh(subscription)  # Это позволяет убедиться, что атрибуты объекта доступны

#     return subscription