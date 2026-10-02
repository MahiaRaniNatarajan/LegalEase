"""Member 2: FastAPI backend for LegalEase.

Endpoints:
    GET  /                 health check
    POST /simplify         simplify pasted legal text (calls Member 1's AI code)
    POST /upload           upload a PDF/DOCX/TXT and get its text back
    POST /export/{fmt}     download text as docx, pdf or txt (uses Member 4's code)
"""
import io
import os
import tempfile

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from ai.gemini_service import simplify_text
from backend.schemas import ExportRequest, SimplifyRequest, SimplifyResponse
from export.docx_export import export_docx
from export.pdf_export import export_pdf
from export.txt_export import export_txt

MAX_CHARS = 30_000

app = FastAPI(title="LegalEase API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a student project; restrict when deployed
    allow_methods=["*"],
    allow_headers=["*"],
)

EXPORTERS = {
    "txt": (export_txt, "text/plain"),
    "docx": (
        export_docx,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
    "pdf": (export_pdf, "application/pdf"),
}


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/simplify", response_model=SimplifyResponse)
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
    except Exception as e:  # AI service failed (bad key, quota, network...)
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
    return {"result": result}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Extract plain text from an uploaded .txt, .docx or .pdf file."""
    name = (file.filename or "").lower()
    data = await file.read()

    try:
        if name.endswith(".txt"):
            text = data.decode("utf-8", errors="ignore")
        elif name.endswith(".docx"):
            from docx import Document

            doc = Document(io.BytesIO(data))
            text = "\n".join(p.text for p in doc.paragraphs)
        elif name.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
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


@app.post("/export/{fmt}")
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

    background.add_task(os.remove, path)  # delete temp file after sending
    return FileResponse(
        path, media_type=media_type, filename=f"{req.filename}.{fmt}"
    )