
# Информационная система "Мониторинг качества воздуха"

## 🛠 Используемые технологии
![Технологии](https://skillicons.dev/icons?i=py,fastapi)

## 📂 Структура проекта
```
air-quality-backend/
├── app
│   ├── bot/
│   │   ├── messages.py       # Заготовки сообщений бота
│   │   └── telegram_bot.py   # Основной функционал телеграм-бота
│   └── db/
│       ├── crud.py           # CRUD операции с базой данных
│       ├── database.py       # Конфигурация базы данных
│       └── models.py         # Таблицы
├── air_quality.py  	      # Запросы к API
├── main.py  			      # Точка входа
└── requirements.txt 	      # Зависимости проекта
```

## Эндпоинты
```
<your-ip-address>/api
├── /get-city  		  # Получение города
├── /get-pollution    # Получение текущего состояния воздуха
├── /get-forecast 	  # Получение состояния воздуха на неделю
└── /subscribe 		  # Forced отправка уведомления в telegram (test-endpoint)
```

## ⚡ Запуск проекта (DEVELOPMENT MODE)

#### 📋 Настройка .env
Скопируйте `.env.sample`, переименуйте в `.env` и добавьте свои данные.

#### 🔧 Создание и активация виртуального окружения
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

#### 📌 Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 🚀 Запуск сервера FastAPI
```bash
uvicorn main:app --reload
```
Проект запустится на порту 8000

## 🔄 Развертывание проекта (PRODUCTION MODE / Docker)
Собрать проект можно командой 
```
docker build -t air-quality-backend .
```
