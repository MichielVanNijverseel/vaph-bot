import streamlit as st

def init_session_state():
    defaults = {
        "ocr_text": None,
        "ocr_docs": {},
        "manual_text": "",
        "candidates": None,
        "stoornis_output": None,
        "selected_codes": [],
        "goto": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
