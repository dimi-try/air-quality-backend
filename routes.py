from fastapi import APIRouter, Request
from air_quality import get_city_by_coords, get_city_by_ip, get_air_pollution_data, get_air_pollution_forecast
from app.db import crud
from config import DEFAULT_CITY_RADIUS
from app.db.database import get_db

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

@router.get("/api/map")
async def get_map_cache():
    with get_db() as db:
        map_cache = crud.get_map_cache(db)
        return( [
            {
                "lat": map_cache.location.latitude,
                "lon": map_cache.location.longitude,
                "aqi": map_cache.location.aqi,
                "components": {
                    "co": map_cache.co,
                    "no": map_cache.no,
                    "no2": map_cache.no2,
                    "o3": map_cache.o3,
                    "so2": map_cache.so2,
                    "pm2_5": map_cache.pm2_5,
                    "pm10": map_cache.pm10,
                    "nh3": map_cache.nh3
                },
                "city": map_cache.location.city,
                "radius": map_cache.location.radius if map_cache.location.radius else DEFAULT_CITY_RADIUS
            } for map_cache in map_cache
        ])
