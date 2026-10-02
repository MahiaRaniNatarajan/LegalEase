# LegalEase

AI-powered tool that simplifies legal documents.

## Team and ownership

| Member | Area | Folder | Branch |
|--------|------|--------|--------|
| 1 | Gemini AI integration | `ai/` | `feature/ai-integration` |
| 2 | FastAPI backend | `backend/` | `feature/backend` |
| 3 | Streamlit frontend | `frontend/` | `feature/frontend` |
| 4 | DOCX / PDF / TXT export | `export/` | `feature/document-export` |
| 5 | Integration, testing, deployment | `tests/`, root files | `integration/testing` |

## Setup

```bash
git clone <repo-url>
cd LegalEase
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
cp .env.example .env           # then add your own API key
```

## Run

```bash
uvicorn backend.main:app --reload      # terminal 1
streamlit run frontend/app.py          # terminal 2
```

## Team workflow

1. `git checkout <your-branch>`
2. `git pull origin main` (get the latest before you start)
3. Work ONLY inside your own folder
4. `git add . && git commit -m "clear message" && git push origin <your-branch>`
5. Open a Pull Request into `main` on GitHub; Member 5 reviews and merges

Rules: never push directly to `main`, never commit `.env`, tell the team before touching shared files.
