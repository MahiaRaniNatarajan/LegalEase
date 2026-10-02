"""Member 2: API routes for LegalEase.

    POST /generate      document details -> generated legal document (main feature)
    POST /simplify      legal text -> plain-language version
    POST /upload        .txt/.docx/.pdf -> extracted text
    POST /export/{fmt}  text -> downloadable txt/docx/pdf
"""
import io
import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.schemas import (
    ExportRequest,
    GenerateRequest,
    GenerateResponse,
    SimplifyRequest,
    SimplifyResponse,
)
from export.docx_export import export_docx
from export.pdf_export import export_pdf
from export.txt_export import export_txt

# Member 1's functions. The agreed contract is:
#   generate_document(details: dict) -> str
#   simplify_text(text: str) -> str
try:
    from ai.gemini_service import generate_document
except ImportError:  # temporary placeholder until Member 1 pushes the real one

    def generate_document(details: dict) -> str:
        return (
            f"[PLACEHOLDER] {details['document_type']} between "
            f"{details['party_one']} and {details['party_two']}"
        )


from ai.gemini_service import simplify_text

MAX_CHARS = 30_000

router = APIRouter()

EXPORTERS = {
    "txt": (export_txt, "text/plain"),
    "docx": (
        export_docx,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
    "pdf": (export_pdf, "application/pdf"),
}


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Receive document details, call the AI module, return the document."""
    details = req.model_dump(mode="json")  # plain dict, dates become strings
    try:
        content = generate_document(details)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
    if not content or not str(content).strip():
        raise HTTPException(status_code=502, detail="AI returned an empty document.")
    return {"document_type": req.document_type, "content": content}


@router.post("/simplify", response_model=SimplifyResponse)
def simplify(req: SimplifyRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is empty.")
    if len(text) > MAX_CHARS:
        raise HTTPException(
            status_code=413, detail=f"Text too long (max {MAX_CHARS} characters)."
        )
    try:
        result = simplify_text(text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
    return {"result": result}


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    data = await file.read()
    try:
        if name.endswith(".txt"):
            text = data.decode("utf-8", errors="ignore")
        elif name.endswith(".docx"):
            from docx import Document

            text = "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
        elif name.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            text = "\n".join((pg.extract_text() or "") for pg in reader.pages)
        else:
            raise HTTPException(
                status_code=415, detail="Only .txt, .docx and .pdf files are supported."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read file: {e}")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="No readable text found in file.")
    return {"filename": file.filename, "text": text[:MAX_CHARS]}


@router.post("/export/{fmt}")
def export(fmt: str, req: ExportRequest, background: BackgroundTasks):
    fmt = fmt.lower()
    if fmt not in EXPORTERS:
        raise HTTPException(status_code=400, detail="Format must be txt, docx or pdf.")
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Nothing to export.")

    func, media_type = EXPORTERS[fmt]
    fd, path = tempfile.mkstemp(suffix=f".{fmt}")
    os.close(fd)
    try:
        func(req.content, path)
    except Exception as e:
        os.remove(path)
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")

    background.add_task(os.remove, path)
    return FileResponse(path, media_type=media_type, filename=f"{req.filename}.{fmt}")