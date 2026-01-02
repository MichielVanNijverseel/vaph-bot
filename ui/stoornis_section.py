import streamlit as st
from utils.llm import run_chat, load_prompt
from logic.code_extraction import extract_codes_from_output
from logic.context_builder import get_patient_context
from utils.vaph_questions import get_stoornis_info, get_all_stoornissen

def get_candidate_by_code(candidates, code):
    """Helper to find candidate info by code."""
    for c in candidates:
        if c['code'] == code:
            return c
    return None

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
        # Extract codes from output and set as selected
        codes = extract_codes_from_output(output)
        st.session_state["selected_codes"] = codes

    if not st.session_state.get("stoornis_output"):
        return

    st.markdown('<a id="stoornissen_section"></a>', unsafe_allow_html=True)
    st.subheader("3️⃣ Geselecteerde stoornissen")

    # Initialize selected_codes if not exists
    if "selected_codes" not in st.session_state:
        codes = extract_codes_from_output(st.session_state["stoornis_output"])
        st.session_state["selected_codes"] = codes
    
    selected_codes = st.session_state.get("selected_codes", [])
    
    # Show model output in expander
    with st.expander("📋 Geselecteerde stoornissen door LLM", expanded=False):
        st.text_area(
            "LLM Output",
            st.session_state["stoornis_output"],
            height=200,
            key="stoornis_output_display",
            label_visibility="collapsed"
        )

    # Display selected codes in dropdown with remove button
    if selected_codes:
        st.markdown("**Verwijder stoornis:**")
        st.caption(f"Huidig aantal geselecteerde stoornissen: {len(selected_codes)}")
        
        # Create dropdown options with format: "Code - Name"
        selected_dropdown_options = []
        selected_option_to_code = {}
        
        for code in selected_codes:
            # First try to get from CSV (full database)
            stoornis_info = get_stoornis_info(code)
            if stoornis_info:
                display_text = f"{code} - {stoornis_info['name']}"
            else:
                # Fallback to candidates if not in CSV (shouldn't happen normally)
                candidate = get_candidate_by_code(candidates, code)
                if candidate:
                    display_text = f"{code} - {candidate['name']}"
                else:
                    display_text = f"{code} (niet gevonden)"
            selected_dropdown_options.append(display_text)
            selected_option_to_code[display_text] = code
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_to_remove = st.selectbox(
                "Selecteer een stoornis om te verwijderen",
                options=selected_dropdown_options,
                key="remove_stoornis_dropdown",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("❌ Verwijder", key="remove_stoornis_btn"):
                if selected_to_remove and selected_to_remove in selected_option_to_code:
                    code_to_remove = selected_option_to_code[selected_to_remove]
                    st.session_state["selected_codes"] = [
                        c for c in st.session_state["selected_codes"] 
                        if c != code_to_remove
                    ]
                    st.rerun()
    else:
        st.info("ℹ️ Geen stoornissen geselecteerd. Voeg er een toe uit de lijst hieronder.")

    st.divider()

    # Show remaining candidates (not in selected) in a dropdown
    selected_set = set(selected_codes)
    remaining_candidates = [
        c for c in candidates 
        if c['code'] not in selected_set
    ]

    if remaining_candidates or len(selected_codes) < 7:
        st.markdown("**Voeg stoornis toe:**")
        st.caption(f"Je kunt maximaal 2 extra stoornissen toevoegen. Huidig aantal: {len(selected_codes)}")
        
        # Dropdown for remaining candidates
        if remaining_candidates:
            # Create dropdown options with format: "Code - Name"
            dropdown_options = [
                f"{c['code']} - {c['name']}" 
                for c in remaining_candidates
            ]
            
            # Create a mapping from display string to code
            option_to_code = {
                f"{c['code']} - {c['name']}": c['code']
                for c in remaining_candidates
            }
            
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_option = st.selectbox(
                    "Selecteer een stoornis om toe te voegen",
                    options=dropdown_options,
                    key="add_stoornis_dropdown",
                    label_visibility="collapsed",
                    disabled=len(selected_codes) >= 7
                )
            
            with col2:
                if len(selected_codes) >= 7:
                    st.button(
                        "➕ Toevoegen",
                        key="add_stoornis_btn",
                        disabled=True,
                        help="Maximum aantal stoornissen bereikt (7)"
                    )
                else:
                    if st.button("➕ Toevoegen", key="add_stoornis_btn"):
                        if selected_option and selected_option in option_to_code:
                            code_to_add = option_to_code[selected_option]
                            if code_to_add not in st.session_state["selected_codes"]:
                                st.session_state["selected_codes"].append(code_to_add)
                                st.rerun()
        
        # Dropdown with all available stoornissen (not in top 15)
        st.markdown("**Of selecteer uit alle beschikbare stoornissen:**")
        
        # Get all stoornissen from CSV
        all_stoornissen = get_all_stoornissen()
        
        # Filter out already selected codes
        selected_set = set(selected_codes)
        available_stoornissen = [
            s for s in all_stoornissen 
            if s['code'] not in selected_set
        ]
        
        if available_stoornissen:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Search/filter input - same width as dropdown
                search_term = st.text_input(
                    "🔍 Zoek op code of naam...",
                    key="stoornis_search_filter",
                    placeholder="Typ om te zoeken...",
                    disabled=len(selected_codes) >= 7,
                    label_visibility="collapsed"
                )
            
            with col2:
                # Empty column to align with button below
                st.empty()
            
            # Filter and sort by relevance
            if search_term:
                search_lower = search_term.lower().strip()
                filtered_stoornissen = []
                
                for s in available_stoornissen:
                    code_lower = s['code'].lower()
                    name_lower = s['name'].lower()
                    
                    # Calculate relevance score
                    score = 0
                    if code_lower == search_lower:
                        score = 1000  # Exact code match
                    elif code_lower.startswith(search_lower):
                        score = 500  # Code starts with search
                    elif search_lower in code_lower:
                        score = 300  # Code contains search
                    elif name_lower.startswith(search_lower):
                        score = 200  # Name starts with search
                    elif search_lower in name_lower:
                        score = 100  # Name contains search
                    
                    if score > 0:
                        filtered_stoornissen.append((score, s))
                
                # Sort by relevance (highest first), then by code
                filtered_stoornissen.sort(key=lambda x: (-x[0], x[1]['code']))
                filtered_stoornissen = [s for _, s in filtered_stoornissen]
            else:
                # No search term - show all, sorted by code
                filtered_stoornissen = sorted(available_stoornissen, key=lambda x: x['code'])
            
            if filtered_stoornissen:
                # Create dropdown options with format: "Code - Name"
                all_dropdown_options = [
                    f"{s['code']} - {s['name']}" 
                    for s in filtered_stoornissen
                ]
                
                # Create a mapping from display string to code
                all_option_to_code = {
                    f"{s['code']} - {s['name']}": s['code']
                    for s in filtered_stoornissen
                }
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_all_option = st.selectbox(
                        "Selecteer een stoornis",
                        options=all_dropdown_options,
                        key="add_all_stoornis_dropdown",
                        label_visibility="collapsed",
                        disabled=len(selected_codes) >= 7
                    )
                
                with col2:
                    if len(selected_codes) >= 7:
                        st.button(
                            "➕ Toevoegen",
                            key="add_all_stoornis_btn",
                            disabled=True,
                            help="Maximum aantal stoornissen bereikt (7)"
                        )
                    else:
                        if st.button("➕ Toevoegen", key="add_all_stoornis_btn"):
                            if selected_all_option and selected_all_option in all_option_to_code:
                                code_to_add = all_option_to_code[selected_all_option]
                                if code_to_add not in st.session_state["selected_codes"]:
                                    stoornis_info = get_stoornis_info(code_to_add)
                                    st.session_state["selected_codes"].append(code_to_add)
                                    if stoornis_info:
                                        st.success(f"✅ {code_to_add} - {stoornis_info['name']} toegevoegd!")
                                    st.rerun()
                
                if search_term:
                    st.caption(f"ℹ️ {len(filtered_stoornissen)} resultaten gevonden voor '{search_term}'")
            else:
                st.info(f"ℹ️ Geen resultaten gevonden voor '{search_term}'")
        else:
            st.info("ℹ️ Alle stoornissen zijn al geselecteerd.")
    
    if not remaining_candidates and len(selected_codes) >= 7:
        st.info("ℹ️ Alle kandidaten zijn al geselecteerd en maximum bereikt.")
