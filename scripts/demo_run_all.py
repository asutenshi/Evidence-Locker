#!/usr/bin/env python
"""
Интеграционный скрипт для демонстрации (End-to-End Field Trial Demo).
Запускает последовательно demo_git_collector.py и demo_workflow.py,
покрывая весь сценарий полевых испытаний из project-passport.md.
"""

import subprocess
import sys
import time

# ANSI Escape-последовательности для красивого форматирования в терминале
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner(text):
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}  {text}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")

def run_script(name, args=[]):
    print(f"{YELLOW}Запуск: python scripts/{name} {' '.join(args)}...{RESET}")
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, f"scripts/{name}"] + args,
        capture_output=False,
        text=True
    )
    elapsed = time.time() - start_time
    msg = f"Скрипт {name} завершился за {elapsed:.2f} сек."
    print(f"{CYAN}{msg} Код выхода: {result.returncode}{RESET}\n")
    return result.returncode == 0

def main():
    print_banner("ИНТЕГРАЦИОННЫЙ СЦЕНАРИЙ EVIDENCE LOCKER (ПОЛЕВЫЕ ИСПЫТАНИЯ)")

    print(f"{BOLD}Сценарий полевых испытаний из паспорта проекта:{RESET}")
    print(" 1. Сборщик (Git Collector) считывает коммит и отправляет его в API.")
    print(" 2. Преподаватель просматривает список необработанных (pending) записей.")
    print(" 3. Преподаватель связывает свидетельство с компетенцией 'teamwork'.")
    print(" 4. Преподаватель меняет статус свидетельства на 'reviewed'.")
    print(" 5. Каждое действие логируется в stdout FastAPI в формате JSON Lines.")
    print("-" * 60)

    print(f"\n{YELLOW}{BOLD}ВАЖНО: ПОДГОТОВКА СДВОЕННОГО ЭКРАНА (SPLIT SCREEN){RESET}")
    print("Для полноценной демонстрации рекомендуется открыть второй")
    print("терминал / сплит-скрин")
    print("и запустить вывод логов сервера. Например:")
    print(
        f"  * При локальном запуске: {BOLD}make run{RESET} "
        "(логи выводятся прямо в ту консоль)"
    )
    print(f"  * При запуске в Docker:  {BOLD}sudo docker compose logs -f api{RESET}")
    print(
        "Это позволит вам в реальном времени наблюдать за выводом "
        "JSON-событий в логах."
    )

    prompt = "Настроили сплит-скрин? Нажмите [Enter] для начала демонстрации..."
    input(f"\n{BOLD}{prompt}{RESET}")

    # Шаг 1: Запуск сборщика
    print_banner("ШАГ 1: ОТПРАВКА СВИДЕТЕЛЬСТВА СБОРЩИКОМ")
    print(
        "Сейчас скрипт scripts/demo_git_collector.py считает "
        "последний коммит из репозитория,"
    )
    print("сформирует валидный xAPI Statement и отправит его на сервер.")
    input(f"\n{BOLD}Нажмите [Enter] для запуска сборщика...{RESET}")

    success = run_script("demo_git_collector.py")
    if not success:
        err_msg = (
            "Ошибка на Шаге 1. Убедитесь, что сервер FastAPI "
            "запущен на порту 8000."
        )
        print(f"\033[91m{BOLD}{err_msg}{RESET}")
        sys.exit(1)

    print(f"{GREEN}{BOLD}Ожидаемый результат в логах сервера:{RESET}")
    log_msg = "Во втором терминале должна появиться JSON-строка события"
    print(f"{GREEN}{log_msg} {BOLD}evidence.created{RESET}:")
    print(f'  {BOLD}{{"event": "evidence.created", ...}}{RESET}')

    prompt = "Проверили логи? Нажмите [Enter] для перехода к действиям преподавателя..."
    input(f"\n{BOLD}{prompt}{RESET}")

    # Шаг 2: Получение pending и привязка компетенций
    print_banner("ШАГ 2: ДЕЙСТВИЯ ПРЕПОДАВАТЕЛЯ (ВОРКФЛОУ И РЕВЬЮ)")
    print("Скрипт scripts/demo_workflow.py выполнит следующие шаги:")
    print(
        " 1. Запросит список pending-записей через "
        "GET /api/v1/evidences?review_status=pending"
    )
    print(
        " 2. Свяжет отправленный коммит с компетенцией 'teamwork' через "
        "POST /api/v1/evidences/{id}/competencies"
    )
    print(
        " 3. Переведет статус в 'reviewed' с текстовой заметкой через "
        "PATCH /api/v1/evidences/{id}/review"
    )
    print(" 4. Запросит список проверенных коммитов для подтверждения изменений.")

    input(f"\n{BOLD}Нажмите [Enter] для запуска воркфлоу преподавателя...{RESET}")

    success = run_script("demo_workflow.py")
    if not success:
        print(f"\033[91m{BOLD}Ошибка на Шаге 2.{RESET}")
        sys.exit(1)

    print(f"{GREEN}{BOLD}Ожидаемый результат в логах сервера:{RESET}")
    print("В логах сервера должны появиться еще два JSON-события:")
    print(f" 1. Привязка компетенции ({BOLD}evidence.linked{RESET}):")
    print(
        f'    {BOLD}{{"event": "evidence.linked", "evidence_id": "...", '
        '"competency_id": "teamwork", "proposed_by": "teacher", '
        '"status": "approved"}}{RESET}'
    )
    print(f" 2. Утверждение ревью ({BOLD}evidence.reviewed{RESET}):")
    print(
        f'    {BOLD}{{"event": "evidence.reviewed", "evidence_id": "...", '
        '"actor_id": "...", "note": "..."}}{RESET}'
    )

    print_banner("ПОЛЕВЫЕ ИСПЫТАНИЯ ЗАВЕРШЕНЫ УСПЕШНО")
    print(f"{GREEN}{BOLD}Все шаги демонстрации успешно выполнены!{RESET}")
    msg = (
        "Свидетельство прошло полный жизненный цикл от создания "
        "до проверки и привязки компетенции."
    )
    print(f"{GREEN}{msg}{RESET}\n")

if __name__ == "__main__":
    main()
