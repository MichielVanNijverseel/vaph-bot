import streamlit as st
from utils.ocr import run_ocr_streamlit
from ui.manual_input import render_manual_input
from logic.context_builder import get_patient_context
from logic.normalize_context import normalize_patient_context


def render_ocr_section():
    uploaded_files = st.file_uploader(
        "📄 Upload medische verslagen (PDF, Word, Docx, Txt)",
        type=["pdf", "word", "docx", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("▶️ Start OCR"):
        all_texts = []
        st.session_state["ocr_docs"] = {}

        for uploaded in uploaded_files:
            progress = st.progress(0)
            uploaded.seek(0)
            progress.progress(40)
            ocr_text = run_ocr_streamlit(uploaded)
            progress.progress(100)

            all_texts.append(f"\n\n===== DOCUMENT: {uploaded.name} =====\n\n{ocr_text}")
            st.session_state["ocr_docs"][uploaded.name] = ocr_text

        st.session_state["ocr_text"] = "\n".join(all_texts)
        st.success("OCR verwerkt")

    if st.session_state.get("ocr_text"):
        st.markdown('<a id="ocr_section"></a>', unsafe_allow_html=True)
        st.subheader("1️⃣ OCR-resultaten")

        for name, text in st.session_state["ocr_docs"].items():
            with st.expander(f"📄 OCR-tekst – {name}", expanded=False):
                st.text_area(name, text, height=250)

        render_manual_input()

        with st.expander("🧠 Volledige context die naar de AI gaat", expanded=False):
            st.text_area(
                "AI-context",
                get_patient_context(),
                height=300,
                disabled=True
            )
        # if st.button("🧠 Interpreteer & structureer medische tekst"):
        #     raw_context = get_patient_context()

        #     with st.spinner("Medische context wordt geïnterpreteerd..."):
        #         normalized = normalize_patient_context(raw_context)

        #     st.session_state["normalized_context"] = normalized
        #     st.success("Medische context geïnterpreteerd")

        # if st.session_state.get("normalized_context"):
        #     with st.expander("🧠 Genormaliseerde medische context (voor AI)", expanded=False):
        #         st.text_area(
        #             "Genormaliseerde context",
        #             st.session_state["normalized_context"],
        #             height=350
        #         )

