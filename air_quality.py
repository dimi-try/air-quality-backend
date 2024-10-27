import requests
from config import (
    OPENWEATHER_API_KEY, 
    GEOCODING_URL, 
    OPENWEATHER_GEOCODING_URL, 
    OPENWEATHER_CURRENT_STATUS_URL, 
    OPENWEATHER_FORECAST_URL)


# получаем город по координатам с API
async def get_city_by_coords(lat, lon):
    url = OPENWEATHER_GEOCODING_URL.format(lon=lon, lat=lat)
    response = requests.get(url)
    data = response.json()
    if data:
        return data[0]["name"]
    return None

# получаем город по ip
def get_city_by_ip(ip):
    if ":" in ip:
        ip = ip[:ip.index(":")]

    url = GEOCODING_URL.format(ip=ip)
    response = requests.get(url)
    data = response.json()
    
    # Проверяем, есть ли поле city
    if "city" in data:
        city = data["city"]
    else:
        city = None

    # Проверяем, есть ли поле loc
    loc = data.get("loc")
    if loc:
        # Разделяем координаты на широту и долготу
        lat, lon = map(float, loc.split(","))
    else:
        lat, lon = None, None

    return city, lat, lon

# получаем текущие данные о качестве воздуха с API
async def get_air_pollution_data(lat, lon):
    url = OPENWEATHER_CURRENT_STATUS_URL.format(lat=lat, lon=lon)
    response = requests.get(url)
    return response.json()

# получаем прогноз качества воздуха на пять дней с API
async def get_air_pollution_forecast(lat, lon):
    url = OPENWEATHER_FORECAST_URL.format(lat=lat, lon=lon)
    response = requests.get(url)
    return response.json()
