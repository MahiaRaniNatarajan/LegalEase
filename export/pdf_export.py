"""Member 4: PDF export."""
from fpdf import FPDF


def export_pdf(content: str, path: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, content)
    pdf.output(path)
    return path
