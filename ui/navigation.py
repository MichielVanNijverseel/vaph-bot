import streamlit as st
import streamlit.components.v1 as components


def handle_scroll_navigation():
    """
    Scrollt naar een sectie indien sidebar-navigatie dit vraagt.
    Gebruikt st.session_state["goto"] als target-id.
    """
    target = st.session_state.get("goto")
    if not target:
        return

    components.html(
        f"""
        <script>
        const el = parent.document.getElementById("{target}");
        if (el) {{
            el.scrollIntoView({{ behavior: "smooth", block: "start" }});
        }}
        </script>
        """,
        height=0,
    )

    # Reset zodat het niet blijft scrollen
    st.session_state["goto"] = None
