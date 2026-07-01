import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.db.database import SessionLocal

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_teacher_token() -> str:
    return os.getenv("TEACHER_TOKEN", "secret_teacher_token")


def get_collector_token() -> str:
    return os.getenv("COLLECTOR_TOKEN", "secret-collector-token")


def get_student_token() -> str:
    return os.getenv("STUDENT_TOKEN", "secret-student-token")


def verify_collector_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials.credentials != get_collector_token():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный токен. Требуются права COLLECTOR (Сборщик)",
        )
    return credentials.credentials


def verify_teacher_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials.credentials != get_teacher_token():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный токен. Требуются права TEACHER (Преподаватель)",
        )
    return credentials.credentials


def verify_student_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials.credentials != get_student_token():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный токен. Требуются права STUDENT (Студент)",
        )
    return credentials.credentials


def verify_teacher_or_collector_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Пропускает либо преподавателя, либо сборщика.
    Возвращает строку с ролью, чтобы эндпоинт понимал, кто его вызвал.
    """
    token = credentials.credentials
    if token == get_teacher_token():
        return "teacher"
    elif token == get_collector_token():
        return "collector"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный токен. Требуются права TEACHER или COLLECTOR",
        )
