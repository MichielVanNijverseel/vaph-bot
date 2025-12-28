from utils.llm import run_chat, load_prompt

def normalize_patient_context(raw_context: str) -> str:
    """
    Zet ruwe OCR + manuele input om naar genormaliseerde medische context.
    """
    if not raw_context:
        return ""

    system_prompt = load_prompt("prompts/normalize_system.txt")

    user_prompt = f"""
Hieronder staat OCR-tekst uit één of meerdere medische verslagen.

Zet deze om naar duidelijke medische tekst volgens de instructies.

--- OCR TEKST ---
{raw_context}
"""

    return run_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0
    )
