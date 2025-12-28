import streamlit as st
from utils.retrieval import retrieve_candidate_stoornissen
from logic.context_builder import get_patient_context

def render_similarity_section():
    patient_context = st.session_state.get(
    "normalized_context",
    get_patient_context()  # fallback
)

    if not patient_context:
        st.info("ℹ️ Nog geen patiëntcontext beschikbaar. Voer eerst OCR uit.")
        return

    if patient_context and st.button("🔍 Zoek kandidaat-stoornissen"):
        candidates = retrieve_candidate_stoornissen(
            patient_context,
            top_k=15
        )
        st.session_state["candidates"] = candidates

    candidates = st.session_state.get("candidates")
    if not candidates:
        return

    st.markdown('<a id="candidates_section"></a>', unsafe_allow_html=True)
    st.subheader("2️⃣ Kandidaten uit similarity search")

    for c in candidates:
        st.write(f"- **{c['name']}** – {c['code']}")
