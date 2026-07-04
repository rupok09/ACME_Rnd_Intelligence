from rdkit import Chem
from rdkit.Chem import Draw, rdMolDescriptors, Descriptors, Crippen, AllChem
import pandas as pd

def screen_molecule_degradation(api_name, smiles):
    """
    Takes an API identifier token and SMILES string to parse 
    molecular properties, map active risk structural areas, 
    and output chemical modification predictive schemas.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Molecule could not be loaded. Verify SMILES notation asset: {smiles}")

    mol.SetProp("_Name", api_name)

    # 1. Structure Image Drawing Generation
    img = Draw.MolToImage(mol, size=(450, 350), legend=api_name)

    # 2. Molecular Metrics Extractor
    properties = {
        "Molecule": api_name,
        "Exact mass": round(rdMolDescriptors.CalcExactMolWt(mol), 4),
        "Molecular formula": rdMolDescriptors.CalcMolFormula(mol),
        "Molecular weight": round(Descriptors.MolWt(mol), 4),
        "LogP": round(Crippen.MolLogP(mol), 3),
        "TPSA": round(rdMolDescriptors.CalcTPSA(mol), 2),
        "H-bond donors": rdMolDescriptors.CalcNumHBD(mol),
        "H-bond acceptors": rdMolDescriptors.CalcNumHBA(mol),
        "Rotatable bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
    }
    properties_df = pd.DataFrame([properties])

    # 3. Functional Group Hot-Spot Vulnerability Scanner
    functional_groups = {
        "amide": "C(=O)N",
        "alcohol": "[OX2H]",
        "ether": "COC",
        "pyridine_ring": "n1ccccc1",
        "tertiary_carbon_alcohol": "[C]([O])[C]([C])[C]",
        "acid_sensitive_amide": "[C:1](=O)[N:2]",
    }

    fg_results = []
    for fg_name, smarts in functional_groups.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt:
            matches = mol.GetSubstructMatches(patt)
            fg_results.append({
                "Functional group": fg_name,
                "SMARTS": smarts,
                "Count": len(matches),
                "Possible risk": "Yes" if len(matches) > 0 else "No"
            })
    fg_df = pd.DataFrame(fg_results)

    # 4. Reaction Transformation Core Matrix Execution
    reaction_smarts = {
        "amide_hydrolysis": "[C:1](=O)[N:2]>>[C:1](=O)O.[N:2]",
        "alcohol_oxidation": "[C:1][OH:2]>>[C:1]=O",
        "ether_cleavage": "[C:1]O[C:2]>>[C:1]O.[C:2]O",
    }

    predicted_products = []
    for reaction_name, smarts_rxn in reaction_smarts.items():
        rxn = AllChem.ReactionFromSmarts(smarts_rxn)
        if rxn:
            product_sets = rxn.RunReactants((mol,))
            for product_set in product_sets:
                for product in product_set:
                    try:
                        Chem.SanitizeMol(product)
                        product_smiles = Chem.MolToSmiles(product)
                        product_mass = rdMolDescriptors.CalcExactMolWt(product)
                        product_formula = rdMolDescriptors.CalcMolFormula(product)
                        
                        predicted_products.append({
                            "Parent": api_name,
                            "Reaction": reaction_name,
                            "Predicted product SMILES": product_smiles,
                            "Exact mass": round(product_mass, 4),
                            "Formula": product_formula
                        })
                    except Exception:
                        pass

    products_df = pd.DataFrame(predicted_products)
    if not products_df.empty:
        products_df = products_df.drop_duplicates(subset=["Predicted product SMILES"])

    # 5. Output Payload Matrix Packager
    return {
        "image": img,
        "properties": properties_df,
        "functional_groups": fg_df,
        "degradants": products_df,
        "molecule": mol
    }