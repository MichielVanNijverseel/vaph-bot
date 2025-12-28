import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🚀 Navigatie")

        if st.button("📄 Ga naar OCR"):
            st.session_state["goto"] = "ocr_section"

        if st.session_state.get("candidates"):
            if st.button("🔍 Ga naar Kandidaten"):
                st.session_state["goto"] = "candidates_section"

        if st.session_state.get("stoornis_output"):
            if st.button("🧠 Ga naar Stoornissen"):
                st.session_state["goto"] = "stoornissen_section"

        if st.session_state.get("selected_codes"):
            if st.button("📘 Ga naar Module A"):
                st.session_state["goto"] = "moduleA_section"
