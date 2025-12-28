import streamlit as st
import streamlit.components.v1 as components

def render_layout():
    # Sticky sidebar
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

    # Titel
    st.title("🩺 VAPH Medische Dossier Analyzer")
    st.subheader("AI-ondersteund hulpmiddel voor tamme Tieb")

def render_collapse_button():
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

def inject_collapse_js():
    components.html(
        """
        <script>
        window.collapseAllExpanders = function() {
            const rootDoc = window.parent.document;
            const details = rootDoc.querySelectorAll("details");
            details.forEach(d => d.removeAttribute("open"));
        };
        </script>
        """,
        height=0,
    )
