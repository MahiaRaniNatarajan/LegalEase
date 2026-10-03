# LegalEase – Streamlit Frontend

## Run (2 terminals)

**Terminal 1 – backend** (from the team's project root, the folder that contains `backend/`, `ai/`, `export/`):

    uvicorn backend.main:app --reload --port 8000

**Terminal 2 – frontend** (this folder):

    python -m venv venv
    venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt
    streamlit run app.py

Open http://localhost:8501

If the backend runs elsewhere, set
`LEGALEASE_API=https://your-backend` before starting Streamlit.

## Test the frontend alone (no backend)

Start with `set LEGALEASE_DEMO=1` (Windows) or `LEGALEASE_DEMO=1` (Mac/Linux) before `streamlit run app.py`.
Generate, edit, preview, simplify and upload all work with sample data.
DOCX/PDF downloads are placeholders in this mode.
