#!/usr/bin/env python
"""
Скрипт-сборщик (Git Collector Demo).
Формирует xAPI Statement на основе последнего коммита из локального Git-репозитория
и отправляет его в API Evidence Locker с COLLECTOR_TOKEN.
"""

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

import httpx


def load_env():
    """Загрузка переменных окружения из .env файла."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

def get_last_commit_info():
    """Получение информации о последнем коммите через git log."""
    try:
        # Получаем hash, имя автора, email, дату в ISO формате и тему коммита
        result = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=format:%H|%an|%ae|%aI|%s"],
            capture_output=True,
            text=True,
            check=True
        )
        parts = result.stdout.strip().split("|")
        if len(parts) >= 5:
            return {
                "hash": parts[0],
                "author_name": parts[1],
                "author_email": parts[2],
                "date": parts[3],
                "subject": parts[4]
            }
    except Exception as e:
        print(
            "Предупреждение: Не удалось прочитать локальный git log "
            f"({e}). Используются мок-данные."
        )

    # Мок-данные на случай, если git log не сработал
    return {
        "hash": "84208df62d6a1bda54cc0c52b14443d6daa36336",
        "author_name": "asutenshi",
        "author_email": "zakan.6000@gmail.com",
        "date": datetime.now(timezone.utc).isoformat(),
        "subject": "demo commit: test ingestion and workflows"
    }

def main():
    load_env()

    api_url = os.getenv("API_URL", "http://localhost:8000")
    collector_token = os.getenv("COLLECTOR_TOKEN", "dev_collector_token_secret")

    print("=== Запуск демо-сборщика ===")
    print(f"API URL: {api_url}")
    print(f"Токен сборщика: {collector_token[:5]}***")

    commit = get_last_commit_info()
    msg = f"Найден коммит: {commit['hash'][:8]} от {commit['author_name']}"
    print(f"{msg} ('{commit['subject']}')")

    # Формируем xAPI Statement строго по профилю Evidence Locker
    statement_id = str(uuid.uuid4())
    xapi_statement = {
        "id": statement_id,
        "actor": {
            "account": {
                "name": commit["author_name"]
            },
            "mbox": f"mailto:{commit['author_email']}"
        },
        "verb": {
            "id": "http://adlnet.gov/expapi/verbs/completed"
        },
        "object": {
            "id": f"https://github.com/asutenshi/Evidence-Locker/commit/{commit['hash']}",
            "definition": {
                "type": "commit"
            }
        },
        "context": {
            "project": "practice-project",
            "extensions": {
                "source_system": "git",
                "source_type": "commit",
                "note": commit["subject"]
            }
        },
        "timestamp": commit["date"]
    }

    headers = {
        "Authorization": f"Bearer {collector_token}",
        "Content-Type": "application/json"
    }

    # Отправка POST запроса
    endpoint = f"{api_url}/api/v1/evidences"
    print(f"Отправка xAPI Statement на эндпоинт {endpoint}...")

    try:
        with httpx.Client() as client:
            response = client.post(endpoint, json=xapi_statement, headers=headers)

            if response.status_code == 201:
                print("Успех: Свидетельство успешно отправлено и сохранено!")
                print(f"Статус ответа: {response.status_code}")
                resp_json = json.dumps(
                    response.json(), indent=2, ensure_ascii=False
                )
                print(f"Тело ответа: {resp_json}")
                # Записываем ID созданной записи для других демо-скриптов
                with open("tmp_last_evidence_id.txt", "w") as f:
                    f.write(statement_id)
            else:
                print(f"Ошибка при отправке: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                sys.exit(1)
    except httpx.RequestError as exc:
        print(f"Ошибка сети/соединения при запросе к {exc.request.url!r}: {exc}")
        print(
            "Убедитесь, что сервер FastAPI запущен (например, "
            "через 'make run' или 'docker-compose up')"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
