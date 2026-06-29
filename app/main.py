import os

from fastapi import FastAPI

from app.api.v1.workflow import router as workflow_router
from app.db.database import Base, engine

os.makedirs("./data", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Practice Project API")

app.include_router(workflow_router)

@app.get("/")
def read_root():
    return {"message": "API is running"}
