"""Member 1: Gemini AI integration."""
import os
from dotenv import load_dotenv

load_dotenv()


def simplify_text(legal_text: str) -> str:
    """Take legal text and return a plain-language version.

    TODO (Member 1): call the Gemini API using os.getenv("GEMINI_API_KEY").
    """
    return f"[PLACEHOLDER] Simplified version of: {legal_text[:100]}"
