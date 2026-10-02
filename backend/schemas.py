"""Member 2: Pydantic models that validate everything the frontend sends."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerateRequest(BaseModel):
    """Document details sent by the frontend to /generate."""

    model_config = ConfigDict(str_strip_whitespace=True)

    document_type: str = Field(
        ..., min_length=3, max_length=100, examples=["Rental Agreement"]
    )
    party_one: str = Field(..., min_length=2, max_length=100, examples=["Ravi Kumar"])
    party_two: str = Field(..., min_length=2, max_length=100, examples=["Anita Sharma"])
    jurisdiction: str = Field("India", min_length=2, max_length=100)
    effective_date: Optional[date] = None
    details: str = Field(
        "",
        max_length=5000,
        description="Extra terms, amounts, duration, special clauses, etc.",
    )
    tone: Literal["formal", "simple"] = "formal"


class GenerateResponse(BaseModel):
    document_type: str
    content: str


class SimplifyRequest(BaseModel):
    text: str


class SimplifyResponse(BaseModel):
    result: str


class ExportRequest(BaseModel):
    content: str
    filename: str = "legalease_output"