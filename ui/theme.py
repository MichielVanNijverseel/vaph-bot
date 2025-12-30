import streamlit as st

def inject_dark_mode_fix():
    st.markdown(
        """
        <style>
        /* =========================
           LLM OUTPUT
        ========================= */
        .llm-output {
            padding: 14px;
            border-radius: 8px;
            white-space: pre-wrap;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            border: 1px solid rgba(100, 100, 100, 0.25);
        }

        /* =========================
           VRAGENBLOK
        ========================= */
        .vragenblok {
            padding: 12px;
            border-left: 4px solid;
            border-radius: 6px;
            line-height: 1.5;
        }

        /* -------- Light mode -------- */
        @media (prefers-color-scheme: light) {
            .llm-output {
                background-color: #f7f9fc;
                color: #1f2937;
                border-color: #c7d2fe;
            }

            .vragenblok {
                background-color: #f8fafc;
                color: #1f2937;
                border-left-color: #64748b;
            }
        }

        /* -------- Dark mode -------- */
        @media (prefers-color-scheme: dark) {
            .llm-output {
                background-color: #0f172a;
                color: #e5e7eb;
                border-color: #334155;
            }

            .vragenblok {
                background-color: #020617;
                color: #e5e7eb;
                border-left-color: #94a3b8;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
