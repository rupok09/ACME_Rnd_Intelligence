import requests
from urllib.parse import quote_plus


def make_property(value, source, link):
    return {
        "value": value,
        "source": source,
        "link": link
    }


def search_chembl_records(api_name):
    try:
        search_url = (
            "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json"
            f"?q={quote_plus(api_name)}"
        )

        response = requests.get(search_url, timeout=20)

        if response.status_code != 200:
            return []

        molecules = response.json().get("molecules", [])

        records = []

        for molecule in molecules[:3]:
            chembl_id = molecule.get("molecule_chembl_id")

            if not chembl_id:
                continue

            profile = get_chembl_profile_by_id(chembl_id)

            if profile:
                records.append({
                    "source": "ChEMBL",
                    "record_name": molecule.get("pref_name") or api_name,
                    "record_id": chembl_id,
                    "formula": profile.get("Molecular Formula", {}).get("value", "—"),
                    "molecular_weight": profile.get("Molecular Weight", {}).get("value", "—"),
                    "structure_url": f"https://www.ebi.ac.uk/chembl/api/data/image/{chembl_id}.svg",
                    "link": f"https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id}/",
                    "search_name": api_name,
                    "data": profile
                })

        return records

    except Exception as error:
        print("ChEMBL search error:", error)
        return []


def get_chembl_profile_by_id(chembl_id):
    try:
        detail_url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
        response = requests.get(detail_url, timeout=20)

        if response.status_code != 200:
            return {}

        data = response.json()
        link = f"https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id}/"
        structure_url = f"https://www.ebi.ac.uk/chembl/api/data/image/{chembl_id}.svg"

        molecule_properties = data.get("molecule_properties") or {}
        structures = data.get("molecule_structures") or {}

        results = {
            "ChEMBL ID": make_property(chembl_id, "ChEMBL", link),
            "Structure": make_property(
                f'<img src="{structure_url}" width="120">',
                "ChEMBL",
                link
            ),
            "Molecular Formula": make_property(molecule_properties.get("full_molformula"), "ChEMBL", link),
            "Molecular Weight": make_property(molecule_properties.get("full_mwt"), "ChEMBL", link),
            "Canonical SMILES": make_property(structures.get("canonical_smiles"), "ChEMBL", link),
            "LogP / LogD": make_property(molecule_properties.get("alogp"), "ChEMBL", link),
        }

        acidic_pka = molecule_properties.get("cx_most_apka")
        basic_pka = molecule_properties.get("cx_most_bpka")

        pka_parts = []

        if acidic_pka:
            pka_parts.append(f"Acidic pKa: {acidic_pka}")

        if basic_pka:
            pka_parts.append(f"Basic pKa: {basic_pka}")

        if pka_parts:
            results["pKa"] = make_property("; ".join(pka_parts), "ChEMBL", link)

        return {
            key: value for key, value in results.items()
            if value.get("value") not in [None, "", "None"]
        }

    except Exception as error:
        print("ChEMBL profile error:", error)
        return {}