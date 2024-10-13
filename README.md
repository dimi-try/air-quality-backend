
# Информационную систему мониторинга качества воздуха
Developed by Stylua Inc (c) Developers
- [Jenkneo](https://github.com/Jenkneo)
- [nuafirytiasewo](https://github.com/nuafirytiasewo)

💻 Languages and Tools : ![Технологии](https://skillicons.dev/icons?i=js,html,css,react)

## Струтктура проекта
```
weather-app-backend/
├── air_quality.py  	# Базовый функционал приложения
├── main.py  			# Основной файл приложения
├── telegram_bot.py 	# Работа с телеграм-ботом
└── requirements.txt 	# Зависимости проекта
```

## Эндпоинты
*вот эту шляпу надо будет потом переписать под redoc*
```
<your-ip-address>/api
├── /get-city  		# Получение города
├── /get-pollution  # Получение текущего состояния воздуха
├── /get-forecast 	# Получение состояния воздуха на неделю
└── /subscribe 		# Forced отправка уведомления в telegram (test-endpoint)
```

## Запуск проекта
После скачивания просто установите все зависимости
```
python -r requirements txt
```
и запустите проект.
```
uvicorn main:app --reload
```
Проект запустится на порту 8000
