from fastapi import APIRouter, Request
from air_quality import get_city_by_coords, get_city_by_ip, get_air_pollution_data, get_air_pollution_forecast

router = APIRouter()

@router.get("/api/get-city")
async def get_city(lat: float = None, lon: float = None, request: Request = dict):
    if lat is not None and lon is not None:
        city = await get_city_by_coords(lat, lon)
    else:
        client_ip = request.client.host
        city, lat, lon = get_city_by_ip(client_ip)
        if not city:
            city = "Астрахань"
            lat = "46.377687" 
            lon = "48.053186"
    return {
        "city": city,
        "coordinates": {
            "lat": lat,
            "lon": lon
        }
    }

@router.get("/api/get-pollution")
async def get_pollution(lat: float, lon: float):
    data = await get_air_pollution_data(lat, lon)
    return data

@router.get("/api/get-forecast")
async def get_forecast(lat: float, lon: float):
    data = await get_air_pollution_forecast(lat, lon)
    return data
