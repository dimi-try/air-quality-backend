
# Информационная система "Мониторинг качества воздуха"

## 🛠 Используемые технологии
![Технологии](https://skillicons.dev/icons?i=py,fastapi,postgres)

---

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

---

## Эндпоинты
```
<your-ip-address>/api
├── /get-city  		  # Получение города
├── /get-pollution    # Получение текущего состояния воздуха
├── /get-forecast 	  # Получение состояния воздуха на неделю
└── /subscribe 		  # Forced отправка уведомления в telegram (test-endpoint)
```

---

## ⚡ Запуск проекта (DEVELOPMENT MODE)

#### 📋 Настройка .env
Скопируйте `.env.sample`, переименуйте в `.env` и добавьте свои данные.

#### 🔧 Создание и активация виртуального окружения
Создание 
```bash
python -m venv venv
```
Активация
```bash
venv\Scripts\activate  # Windows
```
```bash
source venv/bin/activate  # Linux/macOS
```

#### 📌 Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 🚀 Запуск сервера FastAPI
```bash
py main.py
```
API будет доступно по адресу:  
📍 `http://localhost:8000`

---

## 🌍 Деплой

Доступны два способа:

### Вариант 1: Docker Compose вручную

1.  Проверьте `docker-compose.yml`
    
2.  Выполните сборку и пуш:
    

```sh
docker compose build
```
```sh
docker compose up -d
```
```sh
docker push <your-dockerhub>
```

### Вариант 2: Автоматически через GitHub Actions

1.  В файле `.github/workflows/docker-deploy.yml` уже всё готово
    
2.  При пуше в `main` ветку произойдёт автоматическая сборка и публикация образа в DockerHub
    

На прод-сервере можете использовать `docker-compose-server.yml` из [репозитория backend](https://github.com/dimi-try/air-quality-backend). Скопируйте `.env.example`, переименуйте в `.env` и добавьте свои данные.

---

## 🔄 Развертывание проекта (PRODUCTION MODE / Docker)
Собрать проект можно командой 
```
docker build -t air-quality-backend .
```
---
## 🛠 Полезные команды

📌 **Просмотр установленных зависимостей**
```bash
pip list
```

💾 **Сохранение зависимостей**
```bash
pip freeze > requirements.txt
```

🗑 **Удаление всех зависимостей**
```bash
pip uninstall -y -r requirements.txt
```

🧹 **Удаление виртуального окружения venv**
```powershell
Get-ChildItem -Path . -Recurse -Directory -Filter "venv" | Remove-Item -Recurse -Force #windows
```

🧹 **Удаление кеша pycache**
```powershell
Get-ChildItem -Recurse -Directory -Include "__pycache__", ".mypy_cache", ".pytest_cache" | Remove-Item -Recurse -Force #windows
Get-ChildItem -Recurse -Include *.pyc | Remove-Item -Force #windows
```

---

💡 **Если у вас есть вопросы или предложения по улучшению проекта, создайте issue!** 🚀