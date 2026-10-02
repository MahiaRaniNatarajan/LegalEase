"""Member 2: request and response models for the LegalEase API."""
from pydantic import BaseModel


class SimplifyRequest(BaseModel):
    text: str


class SimplifyResponse(BaseModel):
    result: str


class ExportRequest(BaseModel):
    content: str
    filename: str = "legalease_output"