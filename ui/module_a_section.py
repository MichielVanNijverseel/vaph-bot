import streamlit as st
from utils.llm import run_chat, load_prompt
from utils.vaph_questions import get_questions_for_code
from logic.context_builder import get_patient_context
from utils.pdf_generator import generate_pdf_for_code

def render_module_a_section():
    codes = st.session_state.get("selected_codes")
    if not codes:
        return

    st.markdown('<a id="moduleA_section"></a>', unsafe_allow_html=True)
    st.subheader("4️⃣ VAPH Module A per stoornis")

    st.write("Geselecteerde codes:", ", ".join(codes))

    vaph_system = load_prompt("prompts/vaph_system.txt")

    if st.button("🔄 Herlaad stoornisvragen CSV"):
        from utils.vaph_questions import reset_questions
        reset_questions()
        st.success("Stoornisvragen herladen!")

    st.divider()

    tabs = st.tabs(codes)

    for idx, code in enumerate(codes):
        with tabs[idx]:
            st.markdown(f"## 📌 Stoorniscode **{code}**")

            vragenblok = get_questions_for_code(code)
            if not vragenblok:
                st.warning(f"⚠️ Geen vragen gevonden voor code {code}")
                continue

            with st.expander("📄 Vragenblok (Module A)", expanded=False):
                st.markdown(
                        f"""
                        <div class="vragenblok">
                            {vragenblok.replace(chr(10), '<br>')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


            if st.button(f"🚀 Genereer antwoorden voor {code}", key=f"gen_{code}"):

                progress = st.progress(0)
                log = st.empty()

                progress.progress(10)
                log.write("🔎 LLM initialiseren...")

                user_prompt = f"""
Stoorniscode: {code}

Medisch dossier:
{st.session_state.get(
    "normalized_context",
    get_patient_context()  # fallback
)}

Vragen voor module A:
{vragenblok}
"""
                progress.progress(50)
                log.write("🤖 Antwoorden worden gegenereerd...")

                vaph_output = run_chat(vaph_system, user_prompt)

                progress.progress(100)
                log.write("✅ Klaar!")

                st.session_state[f"output_{code}"] = vaph_output

            if st.session_state.get(f"output_{code}"):
                with st.expander("🧠 Antwoorden (gegenereerd)", expanded=True):
                    st.markdown(
                        f"""
                        <div class="llm-output">
                        {st.session_state[f"output_{code}"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Download buttons in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label=f"📄 Download TXT voor {code}",
                        data=st.session_state[f"output_{code}"],
                        file_name=f"VAPH_ModuleA_{code}.txt",
                        mime="text/plain",
                        key=f"dl_txt_{code}"
                    )
                
                with col2:
                    # Generate PDF
                    pdf_buffer = generate_pdf_for_code(
                        st.session_state[f"output_{code}"],
                        code
                    )
                    st.download_button(
                        label=f"📑 Download PDF voor {code}",
                        data=pdf_buffer.getvalue(),
                        file_name=f"VAPH_ModuleA_{code}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{code}"
                    )
