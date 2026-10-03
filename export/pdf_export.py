"""Member 4: PDF export."""
"""Member 4: PDF export."""

from fpdf import FPDF


def export_pdf(content: str, path: str) -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Document title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "LEGALEASE", align="C")
    pdf.ln(15)

    # Document content
    for paragraph in content.split("\n"):
        paragraph = paragraph.strip()

        if not paragraph:
            pdf.ln(4)
            continue

        # Numbered sections → heading
        if paragraph[0].isdigit() and "." in paragraph[:4]:
            pdf.set_font("Helvetica", "B", 13)
            pdf.multi_cell(0, 8, paragraph)
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 7, paragraph)
            pdf.ln(3)

    pdf.output(path)

    return path
