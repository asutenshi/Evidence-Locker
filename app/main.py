from fastapi import FastAPI

app = FastAPI(title="Practice Project API")

@app.get("/")
def read_root():
    return {"message": "API is running"}
