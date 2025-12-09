import pandas as pd

_df = None


def load_questions(csv_path="stoornissen/stoornisvragen.csv"):
    """
    Load CSV containing:
    stoorniscode ; stoornisnaam ; stoornisvragen (open text block)
    """
    global _df
    if _df is None:
        _df = pd.read_csv(csv_path, delimiter=";", encoding="latin1")
    return _df


def get_questions_for_code(code: str):
    """
    Return the question block for a specific VAPH stoorniscode.
    Example return: multiline string with the exact vragen voor module A.
    """
    df = load_questions()

    # Ensure string comparison
    code = str(code).strip()

    # Filter on stoorniscode
    row = df[df["stoorniscode"].astype(str).str.strip() == code]

    if row.empty:
        return f"(⚠️ Geen vragen gevonden voor stoorniscode {code})"

    # If kolomnaam is 'stoornisvragen'
    if "stoornisvragen" not in row.columns:
        raise KeyError("Kolom 'stoornisvragen' ontbreekt in stoornisvragen.csv")

    vragen = row.iloc[0]["stoornisvragen"]

    if pd.isna(vragen) or vragen.strip() == "":
        return f"(⚠️ Geen ingevulde vragen voor code {code})"

    return vragen.strip()


def list_available_codes():
    """
    Handy helper → returns all codes present in the CSV.
    """
    df = load_questions()
    return df["stoorniscode"].astype(str).tolist()


# print(get_questions_for_code("M08"))

