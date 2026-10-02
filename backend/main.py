"""Member 2: FastAPI backend."""
from fastapi import FastAPI
from pydantic import BaseModel

from ai.gemini_service import simplify_text

app = FastAPI(title="LegalEase API")


class SimplifyRequest(BaseModel):
    text: str


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/simplify")
def simplify(req: SimplifyRequest):
    return {"result": simplify_text(req.text)}
