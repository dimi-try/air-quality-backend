from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint, Text
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

    # Связь с подписками
    subscriptions = relationship("Subscription", back_populates="location")
    # alerts = relationship("Alert", back_populates="location")

# class MapCache(Base):
#     __tablename__ = "map_cache"
#     id = Column(Integer, primary_key=True)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)  # Внешний ключ на локации
#     created_at = Column(DateTime, default=datetime.utcnow)                      # Дата создания записи
#     expiration_date = Column(DateTime, nullable=False)                          # Дата истечения срока

#     # Связь с локацией
#     location = relationship("Location")

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
