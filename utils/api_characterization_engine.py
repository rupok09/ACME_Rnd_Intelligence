import os
os.environ["RDK_BUILD_HEADLESS"] = "True"
import matplotlib
matplotlib.use("Agg")

# Your existing imports continue below...
from utils.api_properties import PROPERTY_GROUPS
from utils.pubchem import search_pubchem_records
from utils.chembl import search_chembl_records
from utils.drugbank import search_drugbank_records
from utils.source_merger import build_result_table
from rdkit import Chem
from rdkit.Chem import Draw

def get_property_category_map():
    property_category_map = {}
    for category, properties in PROPERTY_GROUPS.items():
        for property_name in properties:
            property_category_map[property_name] = category
    return property_category_map

def find_matching_records(api_name):
    records = []
    pubchem_records = search_pubchem_records(api_name)
    chembl_records = search_chembl_records(api_name)
    drugbank_records = search_drugbank_records(api_name)

    records.extend(pubchem_records)
    records.extend(chembl_records)
    records.extend(drugbank_records)
    return records

def run_api_characterization(selected_properties, selected_records, smiles=None, api_name="Unknown Molecule"):
    """
    Executes cross-database property mapping matrix generation 
    and handles native molecular structure image rendering safely.
    """
    property_category_map = get_property_category_map()

    # Generate the unified baseline database lookup table
    result_df = build_result_table(
        selected_properties=selected_properties,
        property_category_map=property_category_map,
        selected_records=selected_records
    )

    # Safely isolate RDKit graphic pipeline logic inside execution boundaries
    img = None
    if smiles:
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                img = Draw.MolToImage(mol, size=(500, 400), legend=api_name)
        except Exception:
            pass # Fails safely if structural notation is unparsable

    return {
        "image": img,
        "properties": result_df
    }