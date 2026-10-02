"""LegalEase – Streamlit frontend (Member 3).

Talks to the FastAPI backend:
    POST /generate      -> {document_type, content}
    POST /simplify      -> {result}
    POST /upload        -> {filename, text}
    POST /export/{fmt}  -> file bytes (docx / pdf)
"""
import hashlib
import html
import os
import re
from datetime import date

import requests
import streamlit as st

DEFAULT_API = os.getenv("LEGALEASE_API", "http://localhost:8000")
MAX_CHARS = 30_000
DOC_TYPES = [
    "Employment Contract", "Non-Disclosure Agreement (NDA)", "Rental / Lease Agreement",
    "Freelance Service Agreement", "Partnership Agreement", "Sale Agreement",
    "Loan Agreement", "Offer Letter", "Power of Attorney", "Other (type below)",
]
MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}

st.set_page_config(page_title="LegalEase – AI Legal Document Generator",
                   page_icon="⚖️", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------- styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Source+Serif+4:wght@400;600&display=swap');
html, body, .stApp, .stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea,
.stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: 'Sora', sans-serif; }
[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons
    { font-family: 'Material Symbols Rounded' !important; }
#MainMenu, footer, .stAppDeployButton, [data-testid="stAppDeployButton"],
[data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 1.2rem; max-width: 1280px; }

.hero { background: linear-gradient(120deg,#14213d 0%,#1d3557 60%,#0f766e 140%);
        border-radius: 18px; padding: 28px 34px; color: #fff; display: flex;
        align-items: center; gap: 24px; margin-bottom: 18px; }
.hero svg { flex: none; }
.hero h1 { margin: 0; font-size: 2.1rem; font-weight: 700; letter-spacing: -.5px; color:#fff; }
.hero p  { margin: 6px 0 0; color: #cbd5e1; font-size: .98rem; max-width: 640px; }
.pills span { display:inline-block; margin: 12px 8px 0 0; padding: 4px 12px; font-size:.78rem;
              border:1px solid rgba(255,255,255,.35); border-radius: 99px; color:#e2e8f0; }

.panel-title { font-weight: 600; font-size: 1.05rem; margin: 2px 0 8px; }
.paper { background:#fff; color:#1a1a1a; border:1px solid #d9dee8; border-radius: 4px;
         box-shadow: 0 10px 30px rgba(20,33,61,.10); padding: 44px 56px; max-height: 620px;
         overflow-y: auto; font-family:'Source Serif 4', Georgia, serif; line-height: 1.7;
         font-size: 1.02rem; border-top: 5px solid #14213d; }
.paper h4 { font-family:'Source Serif 4', Georgia, serif; font-size: 1.08rem; margin: 22px 0 6px;
            color:#14213d; }
.paper p  { margin: 0 0 10px; text-align: justify; }
.paper p.li { padding-left: 18px; }
.paper.empty { color:#64748b; text-align:center; padding: 90px 40px; border-top-color:#0f766e; }
.stats { color:#64748b; font-size:.82rem; margin: 6px 0 10px; }
.disclaimer { font-size:.78rem; color:#64748b; margin-top: 14px; }
div[data-testid="stForm"] { background:#fff; border-radius: 14px; border:1px solid #e1e6ef; }
.stButton>button, .stDownloadButton>button, .stFormSubmitButton>button { border-radius: 10px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

LOGO = """<svg width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="#fff" stroke-width="3"
stroke-linecap="round" stroke-linejoin="round"><path d="M32 8v44M20 52h24M14 18h36"/>
<path d="M14 18 6 36h16zM50 18l-8 18h16z"/><path d="M6 36a8 5 0 0 0 16 0M42 36a8 5 0 0 0 16 0"/>
<circle cx="32" cy="8" r="2.5" fill="#fff"/></svg>"""

# ---------------------------------------------------------------- state
for k, v in {"api": DEFAULT_API, "demo": os.getenv("LEGALEASE_DEMO") == "1", "doc_type": "", "exports": {}, "plain": "",
             "simplify_input": "", "simplify_out": "", "last_upload": None}.items():
    st.session_state.setdefault(k, v)


# ---------------------------------------------------------------- helpers
def api_url() -> str:
    return st.session_state.api.strip().rstrip("/")


def error_text(r: requests.Response) -> str:
    try:
        d = r.json().get("detail", r.text)
        if isinstance(d, list):  # pydantic validation errors
            d = "; ".join(f"{'.'.join(str(x) for x in e.get('loc', [])[1:])}: {e.get('msg')}" for e in d)
        return str(d)
    except Exception:
        return r.text[:300] or f"HTTP {r.status_code}"


class _Fake:
    """Minimal stand-in for requests.Response used by demo mode."""
    status_code, ok = 200, True

    def __init__(self, data=None, content=b""):
        self._data, self.content, self.text = data, content, str(data)

    def json(self):
        return self._data


def demo_call(path: str, kw: dict):
    """Fake backend responses so the UI can be tested on its own."""
    if path == "/generate":
        j = kw["json"]
        when = j["effective_date"] or "the date of signing"
        body = (f"## {j['document_type']}\n\nThis agreement is made on {when} under the laws of "
                f"{j['jurisdiction']}.\n\nBetween:\n\n{j['party_one']} (First Party)\n\nAnd:\n\n"
                f"{j['party_two']} (Second Party)\n\n1. Purpose:\n\nThe parties agree to the terms below.\n\n"
                f"2. Terms:\n\n- {j['details'] or 'No special terms were provided.'}\n\n"
                "3. Governing Law:\n\nThis agreement is governed by the laws stated above.\n\n"
                f"IN WITNESS WHEREOF, the parties have signed.\n\n(Demo output, written in {j['tone']} style.)")
        return _Fake({"document_type": j["document_type"], "content": body})
    if path == "/simplify":
        return _Fake({"result": "**In plain words:**\n\n- This is a demo summary.\n"
                                "- Each party must follow the terms they agreed to.\n"
                                "- Ask a lawyer if anything is unclear."})
    if path == "/upload":
        name, data = kw["files"]["file"]
        text = data.decode("utf-8", errors="ignore") if name.lower().endswith(".txt") else \
            "Sample text extracted from your file. The Tenant shall indemnify the Landlord against all claims."
        return _Fake({"filename": name, "text": text})
    if path.startswith("/export/"):
        return _Fake(content=kw["json"]["content"].encode())  # placeholder bytes, not a real DOCX/PDF
    return None


def call(path: str, timeout: int = 180, **kw):
    """Call the backend; show a friendly error and return None on failure."""
    if st.session_state.get("demo"):
        return demo_call(path, kw)
    try:
        r = requests.post(f"{api_url()}{path}", timeout=timeout, **kw)
    except requests.ConnectionError:
        st.error(f"Cannot reach the backend at {api_url()}. Start it with "
                 "`uvicorn backend.main:app --reload` and try again.")
        return None
    except requests.Timeout:
        st.error("The backend took too long to respond. Please try again.")
        return None
    if r.status_code >= 400:
        st.error(error_text(r))
        return None
    return r


def bold(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def paper_html(text: str) -> str:
    out = []
    for line in text.splitlines():
        s = html.escape(line.strip())
        if not s:
            continue
        h = re.match(r"^#{1,6}\s+(.*)", s)
        li = re.match(r"^[-*•]\s+(.*)", s)
        if h:
            out.append(f"<h4>{bold(h.group(1))}</h4>")
        elif li:
            out.append(f"<p class='li'>• {bold(li.group(1))}</p>")
        elif re.match(r"^(\d+\.\s*)?[A-Z][A-Za-z ,&/]{2,60}:$", s):
            out.append(f"<h4>{bold(s)}</h4>")
        else:
            out.append(f"<p>{bold(s)}</p>")
    return f"<div class='paper'>{''.join(out)}</div>"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "legalease_document"


# ---------------------------------------------------------------- hero
st.markdown(f"""
<div class="hero">{LOGO}
  <div><h1>LegalEase</h1>
  <p>Draft contracts, NDAs and agreements from a few details. Review the result, edit it
  in place, and download it ready to sign.</p>
  <div class="pills"><span>Generate</span><span>Edit</span><span>Simplify legal text</span>
  <span>TXT · DOCX · PDF</span></div></div>
</div>""", unsafe_allow_html=True)

tab_gen, tab_simp = st.tabs(["📝  Create a document", "🔍  Simplify legal text"])

# =============================================================== GENERATE
with tab_gen:
    left, right = st.columns([5, 7], gap="large")

    with left:
        st.markdown("<div class='panel-title'>Document details</div>", unsafe_allow_html=True)
        with st.form("gen_form"):
            choice = st.selectbox("Document type", DOC_TYPES)
            custom = st.text_input("Custom document type", placeholder="Only used if you chose “Other”")
            c1, c2 = st.columns(2)
            p1 = c1.text_input("First party", placeholder="Ravi Kumar")
            p2 = c2.text_input("Second party", placeholder="Anita Sharma")
            c3, c4 = st.columns(2)
            juris = c3.text_input("Jurisdiction", value="India")
            tone = c4.radio("Language style", ["formal", "simple"], horizontal=True,
                            help="Formal = traditional legal wording. Simple = plain English.")
            c5, c6 = st.columns([3, 2])
            eff = c5.date_input("Effective date", value=date.today(), format="DD/MM/YYYY")
            no_date = c6.checkbox("No date", help="Leave the effective date out")
            details = st.text_area(
                "Terms and details", height=170, max_chars=5000,
                placeholder="Amounts, duration, notice period, special clauses…\n"
                            "e.g. Rent ₹25,000/month; 11-month term; 2 months' deposit; 30 days' notice")
            go = st.form_submit_button("Generate document", type="primary", use_container_width=True)

        if go:
            doc_type = (custom if choice.startswith("Other") else choice).strip()
            problems = []
            if len(doc_type) < 3:
                problems.append("Enter a document type (at least 3 characters).")
            if len(p1.strip()) < 2 or len(p2.strip()) < 2:
                problems.append("Enter the names of both parties (at least 2 characters each).")
            if len(juris.strip()) < 2:
                problems.append("Enter a jurisdiction.")
            for p in problems:
                st.error(p)
            if not problems:
                payload = {"document_type": doc_type, "party_one": p1.strip(), "party_two": p2.strip(),
                           "jurisdiction": juris.strip(), "effective_date": None if no_date else eff.isoformat(),
                           "details": details.strip(), "tone": tone}
                with st.spinner("Drafting your document… this can take up to a minute."):
                    r = call("/generate", json=payload)
                if r:
                    data = r.json()
                    st.session_state.doc_type = data["document_type"]
                    st.session_state.editor = data["content"]
                    st.session_state.exports = {}
                    st.session_state.plain = ""
                    st.toast("Document ready", icon="✅")

    with right:
        st.markdown("<div class='panel-title'>Your document</div>", unsafe_allow_html=True)
        if not st.session_state.doc_type:
            st.markdown("<div class='paper empty'><h4>Nothing drafted yet</h4>"
                        "<p style='text-align:center'>Fill in the details and select "
                        "<b>Generate document</b>. Your draft will appear here.</p></div>",
                        unsafe_allow_html=True)
        else:
            text = st.session_state.editor
            words = len(text.split())
            st.markdown(f"<div class='stats'><b>{html.escape(st.session_state.doc_type)}</b> · "
                        f"{words:,} words · edits update the preview and downloads</div>",
                        unsafe_allow_html=True)
            t_prev, t_edit = st.tabs(["Preview", "Edit"])
            with t_prev:
                st.markdown(paper_html(text), unsafe_allow_html=True)
            with t_edit:
                st.text_area("Edit the document (press Ctrl+Enter to apply)", key="editor", height=560)

            text = st.session_state.editor
            h = hashlib.md5(text.encode()).hexdigest()
            name = slug(st.session_state.doc_type)

            st.markdown("<div class='panel-title' style='margin-top:14px'>Download</div>",
                        unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            d1.download_button("📄 TXT", text, file_name=f"{name}.txt", mime="text/plain",
                               use_container_width=True)
            for col, fmt in ((d2, "docx"), (d3, "pdf")):
                with col:
                    cached = st.session_state.exports.get(fmt)
                    if cached and cached[0] == h:
                        st.download_button(f"⬇️ Save {fmt.upper()}", cached[1], file_name=f"{name}.{fmt}",
                                           mime=MIME[fmt], use_container_width=True, type="primary")
                    elif st.button(f"{'📝' if fmt == 'docx' else '📕'} Prepare {fmt.upper()}",
                                   key=f"prep_{fmt}", use_container_width=True):
                        with st.spinner(f"Building {fmt.upper()}…"):
                            r = call(f"/export/{fmt}", json={"content": text, "filename": name}, timeout=60)
                        if r:
                            st.session_state.exports[fmt] = (h, r.content)
                            st.rerun()

            with st.expander("Explain this document in plain language"):
                if st.button("Simplify my document", key="simp_doc"):
                    if len(text) > MAX_CHARS:
                        st.error(f"Document is too long to simplify (max {MAX_CHARS:,} characters).")
                    else:
                        with st.spinner("Simplifying…"):
                            r = call("/simplify", json={"text": text})
                        if r:
                            st.session_state.plain = r.json()["result"]
                if st.session_state.plain:
                    st.markdown(st.session_state.plain)

        st.markdown("<div class='disclaimer'>AI-generated drafts are not legal advice. "
                    "Have a qualified lawyer review important documents before signing.</div>",
                    unsafe_allow_html=True)

# =============================================================== SIMPLIFY
with tab_simp:
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("<div class='panel-title'>Paste or upload legal text</div>", unsafe_allow_html=True)
        up = st.file_uploader("Upload a .txt, .docx or .pdf file", type=["txt", "docx", "pdf"])
        if up is not None and st.session_state.last_upload != f"{up.name}-{up.size}":
            with st.spinner("Reading file…"):
                r = call("/upload", files={"file": (up.name, up.getvalue())}, timeout=60)
            if r:
                st.session_state.simplify_input = r.json()["text"]
                st.session_state.last_upload = f"{up.name}-{up.size}"
                st.session_state.simplify_out = ""
        st.text_area("Legal text", key="simplify_input", height=330,
                     placeholder="Paste a clause, contract or notice here…")
        if st.button("Simplify", type="primary", use_container_width=True):
            t = st.session_state.simplify_input.strip()
            if not t:
                st.error("Paste some text or upload a file first.")
            elif len(t) > MAX_CHARS:
                st.error(f"Text is too long (max {MAX_CHARS:,} characters).")
            else:
                with st.spinner("Simplifying…"):
                    r = call("/simplify", json={"text": t})
                if r:
                    st.session_state.simplify_out = r.json()["result"]
    with b:
        st.markdown("<div class='panel-title'>Plain-language version</div>", unsafe_allow_html=True)
        if st.session_state.simplify_out:
            with st.container(border=True):
                st.markdown(st.session_state.simplify_out)
            st.download_button("📄 Download as TXT", st.session_state.simplify_out,
                               file_name="simplified.txt", mime="text/plain")
        else:
            st.info("The simplified text will appear here.")
