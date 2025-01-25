
# Информационная система "Мониторинг качества воздуха"

💻 Languages and Tools : ![Технологии](https://skillicons.dev/icons?i=js,html,css,react)

## Струтктура проекта
```
weather-app-backend/
├── app
│   ├── bot/
│   │   ├── messages.py       # Заготовки сообщений бота
│   │   └── telegram_bot.py   # Основной функционал телеграм-бота
│   └── db/
│       ├── crud.py           # CRUD операции с базой данных
│       ├── database.py       # Конфигурация базы данных
│       └── models.py         # Таблицы
├── air_quality.py  	        # Запросы к API
├── main.py  			            # Точка входа
└── requirements.txt 	        # Зависимости проекта
```

## Эндпоинты
```
<your-ip-address>/api
├── /get-city  		  # Получение города
├── /get-pollution  # Получение текущего состояния воздуха
├── /get-forecast 	# Получение состояния воздуха на неделю
└── /subscribe 		  # Forced отправка уведомления в telegram (test-endpoint)
```

## Запуск проекта (DEVELOPMENT MODE)
После скачивания просто установите все зависимости
```
python -r requirements txt
```
В директории репозитория создаете файл .env, в нем необходимо будет прописать следующие параметры
```
OPENWEATHER_API_KEY=<ключ open weather>
TELEGRAM_BOT_TOKEN=<токен телеграм-бота>
GEOCODING_API_KEY=<ключ для работы геокодинга>
DATABASE_USERNAME=<username базы данных Postgres>
DATABASE_PASSWORD=<пароль базы данных Postgres>
DATABASE_HOST=<хост базы данных>
DATABASE_PORT=<порт базы данных>
DATABASE_NAME=<название таблицы>
```
и запустите проект.
```
uvicorn main:app --reload
```
Проект запустится на порту 8000

## Развертывание проекта (PRODUCTION MODE / Docker)
Собрать проект можно командой 
```
docker build -t weather-app-backend .
```
