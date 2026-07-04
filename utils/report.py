import pandas as pd
from io import BytesIO


def create_result_table(api_name, result, source_type):
    return pd.DataFrame({
        "Property": [
            "API Name",
            "IUPAC Name",
            "Molecular Formula",
            "Molecular Weight",
            "Canonical SMILES",
            "XLogP",
            "Topological Polar Surface Area",
            "Primary Source",
            "Extraction Type"
        ],
        "Value": [
            api_name,
            result.get("IUPACName", "Not found"),
            result.get("MolecularFormula", "Not found"),
            result.get("MolecularWeight", "Not found"),
            result.get("CanonicalSMILES", "Not found"),
            result.get("XLogP", "Not found"),
            result.get("TPSA", "Not found"),
            "PubChem",
            source_type
        ],
        "Unit": ["-", "-", "-", "g/mol", "-", "-", "Å²", "-", "-"],
        "Source": [
            "PubChem", "PubChem", "PubChem", "PubChem", "PubChem",
            "PubChem", "PubChem", "Trusted Web Source", source_type
        ],
        "Confidence": ["99%", "99%", "99%", "99%", "98%", "95%", "95%", "99%", "Demo"]
    })


def create_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="API Properties")

    output.seek(0)
    return output