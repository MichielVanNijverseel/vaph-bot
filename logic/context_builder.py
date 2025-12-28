import streamlit as st

MANUAL_HEADER = "===== MANUELE AANVULLING DOOR ARTS ====="

def get_manual_text() -> str:
    text = st.session_state.get("manual_text")
    if not text:
        return ""
    return text.strip()


def get_ocr_text() -> str:
    text = st.session_state.get("ocr_text")
    if not text:
        return ""
    return text.strip()


def get_patient_context() -> str:
    ocr = get_ocr_text()
    manual = get_manual_text()

    if manual:
        return f"{ocr}\n\n{MANUAL_HEADER}\n{manual}"

    return ocr

