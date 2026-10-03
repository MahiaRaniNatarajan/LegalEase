"""Member 2: FastAPI application setup for LegalEase."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router

app = FastAPI(title="LegalEase API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a student project; restrict when deployed
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health():
    return {"status": "ok"}