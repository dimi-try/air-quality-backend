from fastapi import FastAPI
from app.bot.telegram_bot import start_bot, send_notifications
from worker import update_database
from aiocache import cached
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())
    asyncio.create_task(send_notifications())
    asyncio.create_task(update_database())

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

