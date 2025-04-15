# Используем легковесный образ Python на основе Alpine для минимального размера
FROM python:3.12-alpine

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Устанавливаем postgresql-libs для работы psycopg2-binary и asyncpg, затем ставим Python-зависимости
RUN apk add --no-cache postgresql-libs && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY . .

# Указываем команду для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]