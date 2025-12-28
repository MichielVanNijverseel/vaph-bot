import re

CODE_PATTERN = r"\b[A-Z]\d{2,3}\d?\b"

def extract_codes_from_output(text: str) -> list[str]:
    """
    Extraheert stoorniscodes (bv. G35, F70, M480) uit LLM-output
    """
    if not text:
        return []
    return re.findall(CODE_PATTERN, text)
