from fastapi import FastAPI

from app.database import test_database_connection

app = FastAPI(title="Work Order Task API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def database_check():
    result = test_database_connection()
    return {"database": "connected", "test_result": result}