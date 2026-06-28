FROM python:3.12-slim

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:0.2.11 /uv /bin/uv

# Установка рабочей директории
WORKDIR /app

# Копирование файлов конфигурации проекта
COPY pyproject.toml ./

# Установка зависимостей через uv
# Используем --system, так как мы уже находимся в изолированном контейнере
RUN uv pip install --system -r pyproject.toml

# Копирование исходного кода
COPY . /app/

# Проброс порта FastAPI
EXPOSE 8000

# Запуск Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
