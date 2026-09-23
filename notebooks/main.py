from fastapi import FastAPI

app = FastAPI(
    title="CarCare AI",
    description="AI-powered vehicle maintenance assistant",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "CarCare AI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }