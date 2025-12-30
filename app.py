import streamlit as st
from utils.ocr import run_ocr_streamlit
from utils.retrieval import retrieve_candidate_stoornissen
from utils.llm import run_chat, load_prompt
from utils.vaph_questions import get_questions_for_code
from logic.code_extraction import extract_codes_from_output
import streamlit.components.v1 as components
from ui.manual_input import render_manual_input
from logic.context_builder import get_patient_context
from ui.layout import render_layout, render_collapse_button, inject_collapse_js
from ui.sidebar import render_sidebar
from ui.ocr_section import render_ocr_section
from ui.similarity_section import render_similarity_section
from ui.stoornis_section import render_stoornis_section
from ui.module_a_section import render_module_a_section
from ui.navigation import handle_scroll_navigation
from logic.session import init_session_state
from ui.theme import inject_dark_mode_fix

init_session_state()

# ----------------------------------------------------------------
# ⭐ Streamlit App
# ----------------------------------------------------------------
st.set_page_config(page_title="VAPH Analyzer", layout="wide")

inject_dark_mode_fix()

render_layout()
render_collapse_button()

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


# Side-bar: workflow tracker
render_sidebar()

# ----------------------------------------------------------------
# ⭐ OCR section
# ----------------------------------------------------------------
render_ocr_section()

# ----------------------------------------------------------------
# ⭐ Similarity search section
# ----------------------------------------------------------------
render_similarity_section()

# ----------------------------------------------------------------
# ⭐ Stoornis selectie section
# ----------------------------------------------------------------
render_stoornis_section()


# ----------------------------------------------------------------
# ⭐ Module A section
# ----------------------------------------------------------------
render_module_a_section()


# ----------------------------------------------------------------
# ⭐ Global settings section
# ----------------------------------------------------------------

# Sidebar scroll-navigatie afhandelen (na render)
handle_scroll_navigation()

# Inject collapse JS (globaal)
inject_collapse_js()



