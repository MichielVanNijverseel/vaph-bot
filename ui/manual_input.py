import streamlit as st

def render_manual_input():
    """
    UI waarmee arts extra context kan toevoegen aan het dossier.
    """
    st.subheader("✍️ Manuele aanvulling door arts")

    with st.expander("➕ Voeg manuele context toe (optioneel)", expanded=False):

        manual_text = st.text_area(
            "Extra medische informatie, observaties of context",
            value=st.session_state.get("manual_text", ""),
            height=180,
            placeholder=(
                "Bijvoorbeeld:\n"
                "- Patiënt woont alleen\n"
                "- Snelle vermoeidheid bij stappen\n"
                "- Hulpmiddelen reeds geprobeerd\n"
                "- Functionele impact niet volledig beschreven in verslag"
            ),
            key="manual_text_input"
        )

        if st.button("💾 Bewaar manuele aanvulling"):
            st.session_state["manual_text"] = manual_text
            st.success("Manuele aanvulling opgeslagen")

        if st.session_state.get("manual_text"):
            st.caption("ℹ️ Deze tekst wordt meegenomen in alle volgende AI-stappen.")
