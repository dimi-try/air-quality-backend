# Используем официальный образ Python как базовый
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем зависимости для работы с базой данных
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev

# Копируем файлы зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Добавляем путь к локально установленным пакетам в переменную среды PATH
ENV PATH="/root/.local/bin:$PATH"

# Копируем остальной код приложения
COPY . .

RUN pip show uvicorn

# Указываем команду для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
