import streamlit as st
from utils.ocr import run_ocr_streamlit
from utils.retrieval import retrieve_candidate_stoornissen
from utils.llm import run_chat, load_prompt
from utils.vaph_questions import get_questions_for_code
import re
import streamlit.components.v1 as components


def extract_codes_from_output(text: str):
    return re.findall(r"\b[A-Z]\d{2,3}\d?\b", text)
# ----------------------------------------------------------------
# ⭐ Streamlit App

# ===== CSS for sticky sidebar =====
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="VAPH Analyzer", layout="wide")
st.markdown("""
<style>
#collapse-btn {
    position: fixed;
    top: 80px;        /* afstand onder de top bar van streamlit */
    right: 25px;      /* rechts bovenaan */
    z-index: 9999;    /* altijd boven andere UI elementen */
}
</style>
""", unsafe_allow_html=True)

st.title("🩺 VAPH Medische Dossier Analyzer")
st.subheader("AI-ondersteund hulpmiddel voor tamme Tieb")


# 🔽 Collapse-all knop (na titel, maar vóór alle expanders/tabs)
if st.button("🔽 Alles inklappen (Collapse All)"):
    components.html(
        """
        <script>
        if (window.parent && window.parent.collapseAllExpanders) {
            window.parent.collapseAllExpanders();
        }
        </script>
        """,
        height=0,
    )


# Side-bar: workflow tracker
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

    
uploaded_files = st.file_uploader(
    "📄 Upload medische verslagen (PDF)", 
    type=["pdf"], 
    accept_multiple_files=True
)

# -------------------- OCR uitvoeren --------------------
if uploaded_files and st.button("▶️ Start OCR"):
    all_texts = []
    st.session_state["ocr_docs"] = {}

    for uploaded in uploaded_files:
        progress = st.progress(0, text="OCR wordt uitgevoerd...")
        progress.progress(10, text="Bestand inladen...")
        uploaded.seek(0)

        progress.progress(40, text="OCR aan het verwerken...")
        ocr_text = run_ocr_streamlit(uploaded)
        progress.progress(100, text="Klaar!")

        header = f"\n\n===== DOCUMENT: {uploaded.name} =====\n\n"
        all_texts.append(header + ocr_text)

        # SLA OP PER DOCUMENT ZODAT WE HET STRAKS KUNNEN TONEN
        st.session_state["ocr_docs"][uploaded.name] = ocr_text

    combined_text = "\n".join(all_texts)
    st.session_state["ocr_text"] = combined_text
    st.success("OCR verwerkt")

# -------------------- OCR tonen (ALTIJD indien beschikbaar) --------------------
if st.session_state.get("ocr_text"):

    st.markdown('<a id="ocr_section"></a>', unsafe_allow_html=True)
    st.subheader("1️⃣ OCR-resultaten")

    # Toon OCR per document
    for filename, text in st.session_state.get("ocr_docs", {}).items():
        with st.expander(f"📄 OCR-tekst – {filename}", expanded=False):
            st.text_area(
                f"OCR-{filename}",
                text,
                height=250,
                key=f"ocr_{filename}"
            )
        st.divider()

    # Gecombineerde OCR tonen
    st.subheader("📚 Gecombineerde OCR-tekst (voor LLM)")
    with st.expander("📚 Gecombineerde OCR-tekst (voor LLM)", expanded=False):
        st.text_area(
            "Combined OCR Text",
            st.session_state["ocr_text"],
            height=400,
            key="combined_ocr"
        )

# ----------------------------------------------------------------
# ⭐ Similarity search section
# ----------------------------------------------------------------

# Load combined OCR text from session_state
combined_text = st.session_state.get("ocr_text")

if combined_text and st.button("🔍 Zoek kandidaat-stoornissen"):
    candidates = retrieve_candidate_stoornissen(combined_text, top_k=15)
    st.session_state["candidates"] = candidates

candidates = st.session_state.get("candidates")
if candidates:
    st.markdown('<a id="candidates_section"></a>', unsafe_allow_html=True)
    st.subheader("2️⃣ Kandidaten uit similarity search")

    for c in candidates:
        st.write(f"- **{c['name']}** – {c['code']}")

if candidates:
    stoornis_system = load_prompt("prompts/stoornis_system.txt")

    if st.button("🤖 Laat model max. 5 stoornissen selecteren"):
        candidate_block = "\n".join(
            f"{i+1}. {c['name']} – {c['code']}\nContext: {c['context']}"
            for i, c in enumerate(candidates)
        )

        user_prompt = f"""
        --- MEDISCH DOSSIER ---
        {st.session_state['ocr_text']}
        --- KANDIDAAT-STOORNISSEN ---
        {candidate_block}
        """
        output = run_chat(stoornis_system, user_prompt)
        st.session_state["stoornis_output"] = output

if st.session_state.get("stoornis_output"):
    st.markdown('<a id="stoornissen_section"></a>', unsafe_allow_html=True)
    st.subheader("3️⃣ Geselecteerde stoornissen")
    st.text_area("Modeloutput", st.session_state["stoornis_output"], height=200)
    

    codes = extract_codes_from_output(st.session_state["stoornis_output"])
    st.session_state["selected_codes"] = codes

if st.session_state.get("selected_codes"):
    st.markdown('<a id="moduleA_section"></a>', unsafe_allow_html=True)
    st.subheader("4️⃣ VAPH Module A per stoornis")

    codes = st.session_state["selected_codes"]
    st.write("Geselecteerde codes:", ", ".join(codes))

    vaph_system = load_prompt("prompts/vaph_system.txt")


    # Herladen CSV
    if st.button("🔄 Herlaad stoornisvragen CSV"):
        global _df
        _df = None
        st.success("Stoornisvragen herladen!")

    st.divider()

    # Een tab per stoornis
    tabs = st.tabs(codes)

    for idx, code in enumerate(codes):
        with tabs[idx]:
            st.markdown(f"## 📌 Stoorniscode **{code}**")

            vragenblok = get_questions_for_code(code)
            if not vragenblok:
                st.warning(f"⚠️ Geen vragen gevonden voor code {code}")
                continue

            # Collapsible vragen
            with st.expander("📄 Vragenblok (Module A)", expanded=False):
                st.markdown(
                    f"<div style='padding:10px;border-left:3px solid #999;background:#fafafa'>{vragenblok.replace(chr(10), '<br>')}</div>",
                    unsafe_allow_html=True
                )

            # Genereer antwoorden
            if st.button(f"🚀 Genereer antwoorden voor {code}", key=f"gen_{code}"):

                progress = st.progress(0)
                log = st.empty()

                progress.progress(10)
                log.write("🔎 LLM initialiseren...")

                user_prompt = f"""
Stoorniscode: {code}

Medisch dossier:
{st.session_state['ocr_text']}

Vragen voor module A:
{vragenblok}
"""

                progress.progress(50)
                log.write("🤖 Antwoorden worden gegenereerd...")

                vaph_output = run_chat(vaph_system, user_prompt)

                progress.progress(100)
                log.write("✅ Klaar!")

                st.session_state[f"output_{code}"] = vaph_output

            # Toon output
            if st.session_state.get(f"output_{code}"):
                with st.expander("🧠 Antwoorden (gegenereerd)", expanded=True):
                    st.markdown(
                        f"""
                        <div style="
                            border:1px solid #4a90e2;
                            padding:12px;
                            border-radius:8px;
                            background-color:#f0f7ff;
                            white-space:pre-wrap;
                            font-family:monospace;
                        ">
                        {st.session_state[f"output_{code}"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.download_button(
                    label=f"📥 Download rapport voor {code}",
                    data=st.session_state[f"output_{code}"],
                    file_name=f"VAPH_ModuleA_{code}.txt",
                    mime="text/plain",
                    key=f"dl_{code}"
                )


### Helper to navigate to sections
if "goto" in st.session_state and st.session_state["goto"]:
    components.html(
        f"""
        <script>
        const el = parent.document.getElementById("{st.session_state['goto']}");
        if (el) {{
            el.scrollIntoView({{ behavior: "smooth", block: "start" }});
        }}
        </script>
        """,
        height=0,
    )
    st.session_state["goto"] = None

    
# Helemaal ONDERAAN van app.py
components.html(
    """
    <script>
    // Maak globale functie in de parent (Streamlit) context
    window.collapseAllExpanders = function() {
        const rootDoc = window.parent.document;
        const details = rootDoc.querySelectorAll("details");
        details.forEach(d => d.removeAttribute("open"));
    };
    </script>
    """,
    height=0,
)


