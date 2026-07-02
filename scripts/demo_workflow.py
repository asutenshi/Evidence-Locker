#!/usr/bin/env python
"""
Сценарий ревью преподавателя (Teacher Workflow Demo).
Выполняет GET, POST (привязка компетенций) и PATCH (смена статуса) запросы
с использованием TEACHER_TOKEN.
"""

import json
import os
import sys

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

def main():
    load_env()

    api_url = os.getenv("API_URL", "http://localhost:8000")
    teacher_token = os.getenv("TEACHER_TOKEN", "dev_teacher_token_secret")

    print("=== Запуск сценария проверки (Teacher Workflow) ===")
    print(f"API URL: {api_url}")
    print(f"Токен преподавателя: {teacher_token[:5]}***")

    headers = {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }

    # 1. Получаем ID свидетельства для проверки
    evidence_id = None
    if os.path.exists("tmp_last_evidence_id.txt"):
        with open("tmp_last_evidence_id.txt", "r") as f:
            evidence_id = f.read().strip()
        print(f"Обнаружен ID последнего созданного свидетельства: {evidence_id}")

    # 2. Получение списка необработанных (pending) свидетельств
    print("\nШаг 1: Получение списка свидетельств со статусом 'pending'...")
    try:
        with httpx.Client() as client:
            # Сначала получим все pending
            endpoint = f"{api_url}/api/v1/evidences?review_status=pending"
            response = client.get(endpoint, headers=headers)
            if response.status_code != 200:
                print(f"Ошибка при получении списка: {response.status_code}")
                print(response.text)
                sys.exit(1)

            pending_list = response.json()
            print(f"Найдено необработанных свидетельств: {len(pending_list)}")
            for item in pending_list:
                msg = f" - ID: {item['id']} | Пользователь: {item['actor_id']}"
                print(f"{msg} | Источник: {item['source_system']}")

            # Если ID не был прочитан из файла, берем первое из списка
            if not evidence_id and pending_list:
                evidence_id = pending_list[0]['id']
                print(f"Выбрано свидетельство из списка: {evidence_id}")

            if not evidence_id:
                print(
                    "Нет доступных свидетельств для проверки. "
                    "Запустите сначала scripts/demo_git_collector.py"
                )
                sys.exit(1)

            # 3. Привязка компетенции (POST /evidences/{id}/competencies)
            print(
                f"\nШаг 2: Привязка компетенции 'teamwork' к свидетельству "
                f"{evidence_id}..."
            )
            link_payload = {
                "competency_id": "teamwork"
            }
            link_resp = client.post(
                f"{api_url}/api/v1/evidences/{evidence_id}/competencies",
                json=link_payload,
                headers=headers
            )

            if link_resp.status_code == 201:
                print("Успех: Компетенция успешно привязана!")
                resp_json = json.dumps(
                    link_resp.json(), indent=2, ensure_ascii=False
                )
                print(f"Ответ сервера: {resp_json}")
            else:
                print(f"Ошибка при привязке компетенции: {link_resp.status_code}")
                print(link_resp.text)
                sys.exit(1)

            # 4. Смена статуса на reviewed (PATCH /evidences/{id}/review)
            print("\nШаг 3: Смена статуса свидетельства на 'reviewed'...")
            review_payload = {
                "status": "reviewed",
                "note": (
                    "Коммит проверен и успешно привязан "
                    "к компетенции teamwork преподавателем."
                ),
            }
            review_resp = client.patch(
                f"{api_url}/api/v1/evidences/{evidence_id}/review",
                json=review_payload,
                headers=headers
            )

            if review_resp.status_code == 200:
                print("Успех: Статус свидетельства изменен на 'reviewed'!")
                resp_json = json.dumps(
                    review_resp.json(), indent=2, ensure_ascii=False
                )
                print(f"Ответ сервера: {resp_json}")
            else:
                print(f"Ошибка при изменении статуса: {review_resp.status_code}")
                print(review_resp.text)
                sys.exit(1)

            # 5. Проверка изменений (GET /evidences со статусом reviewed)
            print(
                "\nШаг 4: Проверка изменений через GET-запрос со статусом "
                "'reviewed'..."
            )
            check_endpoint = f"{api_url}/api/v1/evidences?review_status=reviewed"
            check_resp = client.get(check_endpoint, headers=headers)
            if check_resp.status_code == 200:
                reviewed_list = check_resp.json()
                found = any(item["id"] == evidence_id for item in reviewed_list)
                if found:
                    print(
                        f"Подтверждение: Свидетельство {evidence_id} теперь "
                        "находится в списке проверенных (reviewed)!"
                    )
                    # Удалим временный файл
                    if os.path.exists("tmp_last_evidence_id.txt"):
                        os.remove("tmp_last_evidence_id.txt")
                else:
                    print(
                        f"Внимание: Свидетельство {evidence_id} не найдено "
                        "в списке проверенных."
                    )
            else:
                print(f"Ошибка при проверке статуса: {check_resp.status_code}")
                print(check_resp.text)

    except httpx.RequestError as exc:
        print(f"Ошибка сети/соединения при запросе к {exc.request.url!r}: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
