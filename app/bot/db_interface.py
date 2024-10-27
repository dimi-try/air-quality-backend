from app.db.database import get_db
import app.db.crud as crud


def create_or_update_subscription(message, city, coordinates, current_aqi):
  with get_db() as db:
    telegram_id = message.from_user.id
    # Используем функцию create_or_update_subscription
    crud.create_or_update_subscription(
      db,
      telegram_id,
      city,
      lon = coordinates["lon"],
      lat = coordinates["lat"],
      current_aqi = current_aqi
      )