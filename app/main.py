import os

from fastapi import FastAPI

from app.api.v1 import ingestion
from app.db.database import Base, engine

os.makedirs("./data", exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Evidence Locker API", description="Хранилище свидетельств в формате xAPI"
)

app.include_router(ingestion.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Evidence Locker MVP is running"}
