from fastapi import FastAPI

app = FastAPI(title="Work Order Task API")


@app.get("/health")
def health_check():
    return {"status": "ok"}