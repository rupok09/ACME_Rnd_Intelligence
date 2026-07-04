import re
import requests
from urllib.parse import quote_plus


HEADERS = {
    "User-Agent": "ACME-RND-Intelligence/1.0"
}


def make_property(value, source, link):
    return {
        "value": value,
        "source": source,
        "link": link
    }


def search_pubchem_records(api_name):
    try:
        cid_url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
            f"{quote_plus(api_name)}/cids/JSON"
        )

        response = requests.get(cid_url, headers=HEADERS, timeout=20)

        if response.status_code != 200:
            return []

        cid_list = response.json().get("IdentifierList", {}).get("CID", [])

        records = []

        for cid in cid_list[:3]:
            profile = get_pubchem_profile_by_cid(cid, api_name)

            if profile:
                records.append({
                    "source": "PubChem",
                    "record_name": api_name,
                    "record_id": f"CID {cid}",
                    "formula": profile.get("Molecular Formula", {}).get("value", "—"),
                    "molecular_weight": profile.get("Molecular Weight", {}).get("value", "—"),
                    "structure_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG",
                    "link": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
                    "search_name": api_name,
                    "data": profile
                })

        return records

    except Exception as error:
        print("PubChem search error:", error)
        return []


def get_pubchem_profile_by_cid(cid, api_name):
    try:
        property_url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
            f"{cid}/property/"
            "MolecularFormula,MolecularWeight,IUPACName,"
            "CanonicalSMILES,InChI,XLogP,TPSA/JSON"
        )

        response = requests.get(property_url, headers=HEADERS, timeout=20)

        if response.status_code != 200:
            return {}

        profile = response.json()["PropertyTable"]["Properties"][0]
        link = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
        structure_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"

        results = {
            "API Name": make_property(api_name, "PubChem", link),
            "Structure": make_property(
                f'<img src="{structure_url}" width="120">',
                "PubChem",
                link
            ),
            "PubChem CID": make_property(cid, "PubChem", link),
            "Molecular Formula": make_property(profile.get("MolecularFormula"), "PubChem", link),
            "Molecular Weight": make_property(profile.get("MolecularWeight"), "PubChem", link),
            "IUPAC Name": make_property(profile.get("IUPACName"), "PubChem", link),
            "Canonical SMILES": make_property(profile.get("CanonicalSMILES"), "PubChem", link),
            "InChI": make_property(profile.get("InChI"), "PubChem", link),
            "LogP / LogD": make_property(profile.get("XLogP"), "PubChem", link),
        }

        cas_number = get_pubchem_cas(cid)

        if cas_number:
            results["CAS Number"] = make_property(cas_number, "PubChem", link)

        description = get_pubchem_description(cid)

        if description:
            results["Physical Description"] = make_property(description, "PubChem", link)

        return {
            key: value for key, value in results.items()
            if value.get("value") not in [None, "", "None"]
        }

    except Exception as error:
        print("PubChem profile error:", error)
        return {}


def get_pubchem_cas(cid):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
        response = requests.get(url, headers=HEADERS, timeout=20)

        if response.status_code != 200:
            return None

        synonyms = response.json()["InformationList"]["Information"][0].get("Synonym", [])
        cas_pattern = re.compile(r"^\d{2,7}-\d{2}-\d$")

        for synonym in synonyms:
            if cas_pattern.match(synonym):
                return synonym

        return None

    except Exception:
        return None


def get_pubchem_description(cid):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
        response = requests.get(url, headers=HEADERS, timeout=20)

        if response.status_code != 200:
            return None

        information = response.json()["InformationList"]["Information"]

        for item in information:
            if "Description" in item:
                return item["Description"]

        return None

    except Exception:
        return None