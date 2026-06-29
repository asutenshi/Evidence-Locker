from app.db.database import SessionLocal


def get_db():
    """
    Dependency-функция для FastAPI.
    Создает сессию БД для каждого запроса и закрывает её после.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
