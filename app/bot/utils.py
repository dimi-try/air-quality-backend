# Достает lat и lon из сообщения, или возвращает False, если они не найдены
def get_coordinates(message):
  if message.text and "lon" in message.text and "lat" in message.text:
    # Извлекаем координаты из сообщения
    try:
      lon = message.text.split("lon")[1].split("lat")[0].strip()
      lat = message.text.split("lat")[1].strip()

      lon = float(lon.replace("-", "."))
      lat = float(lat.replace("-", "."))

      # Проверка, являются ли координаты широтой и долготой
      if -90 <= lat <= 90 and -180 <= lon <= 180:
        return {"lat": lat, "lon": lon}
      else:
        return False
    except (ValueError, IndexError):
      return False
  else:
    return False
