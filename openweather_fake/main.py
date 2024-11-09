from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# Загрузка данных из файла при запуске сервера
def load_air_data():
    with open("air_data.json", "r") as file:
        data = json.load(file)
    return data

@app.get("/api/air")
async def get_air_data():
    data = load_air_data()
    return JSONResponse(content=data)

# Запуск сервера: `uvicorn filename:app --reload`
