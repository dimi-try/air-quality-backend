from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint, Text, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Связь с подпиской (один пользователь — одна подписка)
    subscription = relationship("Subscription", back_populates="user", uselist=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)  # Unique ограничение
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    # Связи с таблицами Users и Locations
    user = relationship("User", back_populates="subscription")
    location = relationship("Location", back_populates="subscriptions")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    aqi = Column(Integer, nullable=True)
    radius = Column(Integer, nullable=True)
    created_by = Column(
        String(20), 
        nullable=False, 
        default="default"
    )

    # Связь с подписками
    subscriptions = relationship("Subscription", back_populates="location")
    map_cache = relationship("MapCache", back_populates="location", uselist=False)

    # Поле, в которое можно записать от кого была создана запись.
    # Если default - значение не удаляется при удалении подписки пользователя из бд
    # Если telegram_user - значение удаляется при удалении подписки
    # Возможные значения: "telegram_user", "default", другого пока не придумал
    __table_args__ = (
        CheckConstraint("created_by IN ('telegram_user', 'default')", name="check_created_by"),
    )

class MapCache(Base):
    __tablename__ = "map"
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    co = Column(Float, nullable=False)
    no = Column(Float, nullable=False)
    no2 = Column(Float, nullable=False)
    o3 = Column(Float, nullable=False)
    so2 = Column(Float, nullable=False)
    pm2_5 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=False)
    nh3 = Column(Float, nullable=False)

    # Связь с локацией
    location = relationship("Location", back_populates="map_cache", uselist=False)

# Я не уверен что эта таблица нужна...
# class Alert(Base):
#     __tablename__ = "alerts"
#     id = Column(Integer, primary_key=True)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)  # Внешний ключ на локации
#     current_aqi = Column(Integer, nullable=False)                              # Текущий индекс AQI
#     delta_aqi = Column(Integer, nullable=False)                                # Изменение AQI
#     alert_datetime = Column(DateTime, default=datetime.utcnow)                 # Дата и время события
#     message = Column(Text, nullable=False)                                     # Сообщение с уведомлением

#     # Связь с локацией
#     location = relationship("Location", back_populates="alerts")
