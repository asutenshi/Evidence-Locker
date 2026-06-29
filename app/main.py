import os
from fastapi import FastAPI
from app.db.database import engine, Base
from app.db import models

os.makedirs("./data", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Practice Project API")

@app.get("/")
def read_root():
    return {"message": "API is running"}
