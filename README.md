
# Информационную систему мониторинга качества воздуха
Developed by Stylua Inc (c) Developers
- [Jenkneo](https://github.com/Jenkneo)
- [nuafirytiasewo](https://github.com/nuafirytiasewo)

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
*вот эту шляпу надо будет потом переписать под redoc*
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
Примечание! 
Если у вас включен VPN, есть вероятность того, что Docker не подтянет python
Проект будет развернут и запущен, но пока хз где, потому что это не та ветка блен...
