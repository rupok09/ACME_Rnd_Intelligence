import pandas as pd

from utils.pubchem import get_pubchem_profile
from utils.chembl import get_chembl_profile
from utils.drugbank import get_drugbank_placeholder


def make_link(label, url):
    if url:
        return f'<a href="{url}" target="_blank">{label}</a>'
    return "—"


def build_result_row(category, property_name, value, status, sources, links):
    return {
        "Category": category,
        "Property": property_name,
        "Value": value if value not in [None, ""] else "Not Found",
        "Status": status,
        "Source(s)": ", ".join(sources) if sources else "—",
        "Links": " · ".join(links) if links else "—"
    }


def compare_values(primary_value, secondary_value):
    if primary_value and secondary_value:
        if str(primary_value).strip() == str(secondary_value).strip():
            return primary_value, "✅ Found"
        return f"{primary_value} / {secondary_value}", "⚠ Review"

    if primary_value:
        return primary_value, "✅ Found"

    if secondary_value:
        return secondary_value, "✅ Found"

    return "Not Found", "❌ Missing"


def characterize_api(api_name, api_form, selected_properties):
    pubchem = get_pubchem_profile(api_name)
    chembl = get_chembl_profile(api_name)
    drugbank = get_drugbank_placeholder(api_name)

    pubchem_url = pubchem.get("PubChemURL") if pubchem else None
    chembl_url = chembl.get("ChEMBLURL") if chembl else None
    drugbank_url = drugbank.get("DrugBankURL") if drugbank else None

    chembl_props = {}
    if chembl:
        chembl_props = chembl.get("molecule_properties") or {}

    rows = []

    property_category_map = {
        "API Name": "Identity",
        "API Form": "Identity",
        "PubChem CID": "Identity",
        "ChEMBL ID": "Identity",
        "CAS Number": "Identity",
        "Molecular Formula": "Identity",
        "Molecular Weight": "Identity",
        "IUPAC Name": "Identity",
        "Canonical SMILES": "Identity",
        "InChI": "Identity",

        "Physical Description": "Physicochemical",
        "Melting Point": "Physicochemical",
        "Solubility": "Physicochemical",
        "Solubility vs pH": "Physicochemical",
        "pKa": "Physicochemical",
        "LogP / LogD": "Physicochemical",
        "BCS Classification": "Physicochemical",

        "Solid-state Form / Polymorph": "Solid State",
        "Hygroscopicity": "Solid State",
        "Bulk Density": "Solid State",
        "Tapped Density": "Solid State",
        "Flowability": "Solid State",

        "Photostability": "Stability",
        "Chemical Stability - Solid State": "Stability",
        "Chemical Stability - Solution": "Stability",
        "Forced Degradation Data": "Stability",
    }

    for prop in selected_properties:
        category = property_category_map.get(prop, "Other")

        value = "Not Found"
        status = "❌ Missing"
        sources = []
        links = []

        if prop == "API Name":
            value = api_name
            status = "✅ Found"
            sources = ["User Input"]

        elif prop == "API Form":
            value = api_form
            status = "✅ Found"
            sources = ["User Input"]

        elif prop == "PubChem CID" and pubchem:
            value = pubchem.get("CID")
            status = "✅ Found"
            sources = ["PubChem"]
            links = [make_link("PubChem", pubchem_url)]

        elif prop == "ChEMBL ID" and chembl:
            value = chembl.get("molecule_chembl_id")
            status = "✅ Found"
            sources = ["ChEMBL"]
            links = [make_link("ChEMBL", chembl_url)]

        elif prop == "CAS Number" and pubchem and pubchem.get("CAS"):
            value = pubchem.get("CAS")
            status = "✅ Found"
            sources = ["PubChem"]
            links = [make_link("PubChem", pubchem_url)]

        elif prop == "Molecular Formula":
            pub_val = pubchem.get("MolecularFormula") if pubchem else None
            chem_val = chembl_props.get("full_molformula") if chembl_props else None
            value, status = compare_values(pub_val, chem_val)

            if pub_val:
                sources.append("PubChem")
                links.append(make_link("PubChem", pubchem_url))
            if chem_val:
                sources.append("ChEMBL")
                links.append(make_link("ChEMBL", chembl_url))

        elif prop == "Molecular Weight":
            pub_val = pubchem.get("MolecularWeight") if pubchem else None
            chem_val = chembl_props.get("full_mwt") if chembl_props else None
            value, status = compare_values(pub_val, chem_val)

            if pub_val:
                sources.append("PubChem")
                links.append(make_link("PubChem", pubchem_url))
            if chem_val:
                sources.append("ChEMBL")
                links.append(make_link("ChEMBL", chembl_url))

        elif prop == "IUPAC Name" and pubchem:
            value = pubchem.get("IUPACName")
            status = "✅ Found"
            sources = ["PubChem"]
            links = [make_link("PubChem", pubchem_url)]

        elif prop == "Canonical SMILES":
            pub_val = pubchem.get("CanonicalSMILES") if pubchem else None
            chem_val = chembl.get("molecule_structures", {}).get("canonical_smiles") if chembl else None
            value, status = compare_values(pub_val, chem_val)

            if pub_val:
                sources.append("PubChem")
                links.append(make_link("PubChem", pubchem_url))
            if chem_val:
                sources.append("ChEMBL")
                links.append(make_link("ChEMBL", chembl_url))

        elif prop == "InChI" and pubchem:
            value = pubchem.get("InChI")
            status = "✅ Found"
            sources = ["PubChem"]
            links = [make_link("PubChem", pubchem_url)]

        elif prop == "Physical Description" and pubchem and pubchem.get("Description"):
            value = pubchem.get("Description")
            status = "✅ Found"
            sources = ["PubChem"]
            links = [make_link("PubChem", pubchem_url)]

        elif prop == "pKa":
            acidic = chembl_props.get("cx_most_apka")
            basic = chembl_props.get("cx_most_bpka")

            if acidic or basic:
                parts = []
                if acidic:
                    parts.append(f"Acidic pKa: {acidic}")
                if basic:
                    parts.append(f"Basic pKa: {basic}")

                value = "; ".join(parts)
                status = "✅ Found"
                sources = ["ChEMBL"]
                links = [make_link("ChEMBL", chembl_url)]

        elif prop == "LogP / LogD":
            pub_val = pubchem.get("XLogP") if pubchem else None
            chem_val = chembl_props.get("alogp") if chembl_props else None
            value, status = compare_values(pub_val, chem_val)

            if pub_val:
                sources.append("PubChem")
                links.append(make_link("PubChem", pubchem_url))
            if chem_val:
                sources.append("ChEMBL")
                links.append(make_link("ChEMBL", chembl_url))

        elif prop in [
            "BCS Classification",
            "Melting Point",
            "Solubility",
            "Solubility vs pH",
            "Solid-state Form / Polymorph",
            "Hygroscopicity",
            "Bulk Density",
            "Tapped Density",
            "Flowability",
            "Photostability",
            "Chemical Stability - Solid State",
            "Chemical Stability - Solution",
            "Forced Degradation Data",
        ]:
            value = "Not Found"
            status = "❌ Missing"
            sources = []
            links = []

        rows.append(
            build_result_row(
                category=category,
                property_name=prop,
                value=value,
                status=status,
                sources=sources,
                links=links
            )
        )

    df = pd.DataFrame(rows)

    return df