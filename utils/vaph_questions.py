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


def reset_questions():
    """
    Reset the cached questions dataframe to force reload from CSV.
    """
    global _df
    _df = None


def get_stoornis_info(code: str):
    """
    Get stoornis name and validate code exists in CSV.
    Returns dict with 'code', 'name', 'exists' or None if not found.
    """
    df = load_questions()
    code = str(code).strip()
    
    row = df[df["stoorniscode"].astype(str).str.strip() == code]
    
    if row.empty:
        return None
    
    return {
        "code": code,
        "name": str(row.iloc[0].get("stoornisnaam", "")),
        "exists": True
    }


def get_all_stoornissen():
    """
    Get all stoornissen from CSV with code and name.
    Returns list of dicts with 'code' and 'name'.
    """
    df = load_questions()
    stoornissen = []
    
    for _, row in df.iterrows():
        code = str(row["stoorniscode"]).strip()
        name = str(row.get("stoornisnaam", "")).strip()
        if code and name:
            stoornissen.append({
                "code": code,
                "name": name
            })
    
    # Sort by code
    stoornissen.sort(key=lambda x: x["code"])
    return stoornissen


# print(get_questions_for_code("M08"))

