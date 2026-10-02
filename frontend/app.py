"""Member 3: Streamlit frontend."""
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("LegalEase")
text = st.text_area("Paste your legal text here")

if st.button("Simplify") and text.strip():
    resp = requests.post(f"{BACKEND_URL}/simplify", json={"text": text})
    st.write(resp.json().get("result", "Error"))
