
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
## 🗄 Резервное копирование базы данных

### 📤 Создание резервной копии

1️⃣ Проверить, существует ли бэкап уже на сервере
```
find / -type f -name "*air_quality*" 2>/dev/null
```

2️⃣ Заходим в контейнер с PostgreSQL:
```
docker exec -it air-postgres-1 bash
```

3️⃣ Делаем дамп базы:
```
pg_dump -U POSTGRES_USER -d air_quality -Fc > /tmp/air_quality_backup.dump
```

4️⃣ Выходим из контейнера:
```
exit
```

5️⃣ Копируем дамп из контейнера на сервер:
```
docker cp air-postgres-1:/tmp/air_quality_backup.dump ./air_quality_backup.dump
```

6️⃣ Скачиваем дамп на локальную машину:

👉 Windows (PowerShell):

```
scp user@server:./air_quality_backup.dump C:\Users\USER\Downloads\
```

👉 Linux/macOS:

```
scp user@server:./air_quality_backup.dump ~/Downloads/
```

7️⃣ Подключаемся снова к серверу и чистим временные файлы:

Удаляем бэкап на сервере:
``` 
rm ./air_quality_backup.dump  
``` 
Заходим в контейнер
``` 
docker exec -it air-postgres-1 bash
```
Удаляем бэкап с контейнера
```
rm /tmp/air_quality_backup.dump
```

8️⃣ Выходим из контейнера:
```
exit
```

9️⃣ Проверить, существует ли бэкап еще на сервере
```
find / -type f -name "*air_quality*" 2>/dev/null
```

---

### 📥 Восстановление из резервной копии

1️⃣ Проверить, существует ли бэкап уже на сервере
```
find / -type f -name "*air_quality*" 2>/dev/null
```

2️⃣ Загружаем дамп на сервер:

👉 Windows (PowerShell):

```
scp C:\Users\USER\Downloads\air_quality_backup.dump user@server:./air_quality_backup.dump
```

👉 Linux/macOS:

```
scp -r ~/Downloads/air_quality_backup.dump user@server:./air_quality_backup.dump
```

3️⃣ Копируем дамп в контейнер:
```
docker cp ./air_quality_backup.dump air-postgres-1:/tmp/air_quality_backup.dump
```

4️⃣ Удаляем старую базу и создаём новую:

Останавливаем бэк
```
docker stop air-backend-1
```
Дропаем бдшку
```
docker exec -it air-postgres-1 psql -U POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS air_quality;"
```
Запускаем заново бэк
```
docker start air-backend-1
```
Пересоздаем бдшку
```
docker exec -it air-postgres-1 psql -U POSTGRES_USER -d postgres -c "CREATE DATABASE air_quality;"

```

5️⃣ Восстанавливаем базу из дампа:

```
docker exec -i air-postgres-1 pg_restore -U POSTGRES_USER -d air_quality --verbose /tmp/air_quality_backup.dump
```

6️⃣ Подключаемся снова к серверу и чистим временные файлы:

Удаляем бэкап на сервере:
``` 
rm ./air_quality_backup.dump  
``` 
Заходим в контейнер
``` 
docker exec -it air-postgres-1 bash
```
Удаляем бэкап с контейнера
```
rm /tmp/air_quality_backup.dump
```

7️⃣ Выходим из контейнера:
```
exit
```

8️⃣ Проверить, существует ли бэкап еще на сервере
```
find / -type f -name "*air_quality*" 2>/dev/null
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