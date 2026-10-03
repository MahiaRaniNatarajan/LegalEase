"""Member 4: PDF export."""

from fpdf import FPDF


FONT_PATH = r"C:\Windows\Fonts\arial.ttf"


def export_pdf(content: str, path: str) -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Unicode font for characters such as ₹
    pdf.add_font("ArialUnicode", "", FONT_PATH)

    # Document title
    pdf.set_font("ArialUnicode", size=20)
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
            pdf.set_font("ArialUnicode", size=13)
            pdf.multi_cell(0, 8, paragraph)
            pdf.ln(2)
        else:
            pdf.set_font("ArialUnicode", size=11)
            pdf.multi_cell(0, 7, paragraph)
            pdf.ln(3)

    pdf.output(path)

    return path