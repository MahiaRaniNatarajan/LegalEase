"""Member 4: DOCX export."""
from docx import Document


def export_docx(content: str, path: str) -> str:
    doc = Document()
    doc.add_paragraph(content)
    doc.save(path)
    return path
