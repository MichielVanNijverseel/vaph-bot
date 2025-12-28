import streamlit as st
from utils.llm import run_chat, load_prompt
from logic.code_extraction import extract_codes_from_output
from logic.context_builder import get_patient_context

def render_stoornis_section():
    candidates = st.session_state.get("candidates")
    if not candidates:
        return

    stoornis_system = load_prompt("prompts/stoornis_system.txt")

    if st.button("🤖 Laat model max. 5 stoornissen selecteren"):
        candidate_block = "\n".join(
            f"{i+1}. {c['name']} – {c['code']}\nContext: {c['context']}"
            for i, c in enumerate(candidates)
        )

        user_prompt = f"""
--- MEDISCH DOSSIER ---
{st.session_state.get(
    "normalized_context",
    get_patient_context()  # fallback
)}
--- KANDIDAAT-STOORNISSEN ---
{candidate_block}
"""
        output = run_chat(stoornis_system, user_prompt)
        st.session_state["stoornis_output"] = output

    if not st.session_state.get("stoornis_output"):
        return

    st.markdown('<a id="stoornissen_section"></a>', unsafe_allow_html=True)
    st.subheader("3️⃣ Geselecteerde stoornissen")

    st.text_area(
        "Modeloutput",
        st.session_state["stoornis_output"],
        height=200
    )

    codes = extract_codes_from_output(st.session_state["stoornis_output"])
    st.session_state["selected_codes"] = codes
