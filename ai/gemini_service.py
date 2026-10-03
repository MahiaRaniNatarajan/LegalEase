"""Gemini AI service for LegalEase legal document generation."""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
def simplify_text(legal_text: str) -> str:
    """Simplify legal text using Gemini."""

    prompt = f"""
You are a legal language assistant for the LegalEase application.

Explain the following legal text in simple, easy-to-understand language.

Legal text:
{legal_text}

Requirements:
1. Keep the original meaning.
2. Do not add legal facts that are not present.
3. Use simple language.
4. Keep the explanation concise.
5. Return only the simplified explanation.
"""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=120000)
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if not response or not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text.strip()

    except Exception as error:
        raise RuntimeError(
            f"Gemini text simplification failed: {error}"
        ) from error


class GeminiDocumentGenerator:
    """Generate legal document drafts using Google Gemini."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")

        self.client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=120000)
)
        self.model = "gemini-3.5-flash-lite"

    def _generate_document(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the generated document."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if not response or not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text.strip()

        except Exception as error:
            raise RuntimeError(
                f"Gemini document generation failed: {error}"
            ) from error

    def generate_employment_contract(self, data: dict) -> str:
        """Generate an employment contract."""

        prompt = f"""
You are a legal document drafting assistant for the LegalEase application.

Generate a professional EMPLOYMENT CONTRACT using the information below.

Information:
{data}

Requirements:
1. Use clear and professional legal language.
2. Do not invent information that is not provided.
3. Use [NOT PROVIDED] for missing information.
4. Organize the document with numbered sections.
5. Include:
   - Employer and employee details
   - Job title and responsibilities
   - Employment terms
   - Salary and benefits
   - Working hours
   - Leave
   - Confidentiality
   - Termination
   - Applicable law
   - Signatures
6. Use a clear title.
7. End with signature sections for both parties.
8. This is an AI-generated draft and should be reviewed by a qualified legal professional.

Return only the document.
"""

        return self._generate_document(prompt)

    def generate_nda(self, data: dict) -> str:
        """Generate a Non-Disclosure Agreement."""

        prompt = f"""
You are a legal document drafting assistant for the LegalEase application.

Generate a professional NON-DISCLOSURE AGREEMENT (NDA) using the information below.

Information:
{data}

Requirements:
1. Use clear and professional legal language.
2. Do not invent information that is not provided.
3. Use [NOT PROVIDED] for missing information.
4. Organize the document using numbered sections.
5. Include exactly these sections in this order:
   1. Parties
   2. Purpose
   3. Definition of Confidential Information
   4. Obligations of the Receiving Party
   5. Exclusions from Confidential Information
   6. Duration of Confidentiality
   7. Return or Destruction of Information
   8. Breach and Remedies
   9. Applicable Law
   10. Disclaimer
   11. Signatures
6. Use a clear title: NON-DISCLOSURE AGREEMENT.
7. The Signatures section must be the final section.
8. Under the Signatures section, provide separate signature blocks for:
   - Disclosing Party
   - Receiving Party
   Include name, signature, and date fields.
9. Do not create any additional numbered sections.
10. This is an AI-generated draft and should be reviewed by a qualified legal professional.

Return only the document.
"""

        return self._generate_document(prompt)

    def generate_lease_agreement(self, data: dict) -> str:
        """Generate a lease agreement."""

        prompt = f"""
You are a legal document drafting assistant for the LegalEase application.

Generate a professional LEASE AGREEMENT using the information below.

Information:
{data}

Requirements:
1. Use clear and professional legal language.
2. Do not invent information that is not provided.
3. Use [NOT PROVIDED] for missing information.
4. Organize the document with numbered sections.
5. Include:
   - Landlord and tenant details
   - Property details
   - Lease duration
   - Rent and payment terms
   - Security deposit
   - Utilities and maintenance
   - Permitted use
   - Tenant responsibilities
   - Termination
   - Applicable law
   - Signatures
6. Use a clear title.
7. End with signature sections for both parties.
8. This is an AI-generated draft and should be reviewed by a qualified legal professional.

Return only the document.
"""

        return self._generate_document(prompt)
def generate_document(details: dict) -> str:
    """Adapter used by the FastAPI backend to generate supported documents."""

    generator = GeminiDocumentGenerator()

    document_type = details.get("document_type", "").strip().lower()

    data = {
        "party_one": details.get("party_one", ""),
        "party_two": details.get("party_two", ""),
        "jurisdiction": details.get("jurisdiction", "India"),
        "effective_date": details.get("effective_date"),
        "details": details.get("details", ""),
        "tone": details.get("tone", "formal"),
    }

    if "employment" in document_type:
        return generator.generate_employment_contract(data)

    if "nda" in document_type or "non-disclosure" in document_type:
        return generator.generate_nda(data)

    if "lease" in document_type or "rental" in document_type:
        return generator.generate_lease_agreement(data)

    raise ValueError(
        "Unsupported document type. Supported types are "
        "Employment Contract, NDA, and Lease Agreement."
    )


if __name__ == "__main__":
    generator = GeminiDocumentGenerator()

    nda_data = {
        "disclosing_party": "ABC Technologies",
        "receiving_party": "John Doe",
        "purpose": "Software development employment",
        "confidentiality_period": "2 years"
    }

    document = generator.generate_nda(nda_data)

    print(document)