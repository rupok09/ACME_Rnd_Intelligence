from rdkit import Chem
from rdkit.Chem import (
    rdMolDescriptors,
    Descriptors,
    Crippen,
    AllChem,
)
from rdkit.Chem.Draw import rdMolDraw2D

import pandas as pd


# ==========================================================
# SVG Structure Generator
# ==========================================================

def molecule_to_svg(mol, legend=""):
    """
    Generate SVG representation of a molecule.
    Compatible with headless Linux servers.
    """

    drawer = rdMolDraw2D.MolDraw2DSVG(500, 400)

    rdMolDraw2D.PrepareAndDrawMolecule(
        drawer,
        mol,
        legend=legend
    )

    drawer.FinishDrawing()

    svg = drawer.GetDrawingText()

    return svg


# ==========================================================
# Main RDKit Engine
# ==========================================================

def screen_molecule_degradation(api_name, smiles):
    """
    Screen an API molecule for:

    • Molecular descriptors
    • Functional groups
    • Potential degradation hot-spots
    • Simple degradation products

    Returns a dictionary containing:

    image (SVG)

    molecular properties

    functional groups

    predicted degradants

    RDKit molecule object
    """

    # ------------------------------------------------------
    # Build Molecule
    # ------------------------------------------------------

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        raise ValueError(
            f"Unable to parse SMILES:\n{smiles}"
        )

    mol.SetProp("_Name", api_name)

    # ------------------------------------------------------
    # SVG Structure
    # ------------------------------------------------------

    structure_svg = molecule_to_svg(
        mol,
        legend=api_name
    )

    # ------------------------------------------------------
    # Molecular Properties
    # ------------------------------------------------------

    properties = {

        "Molecule": api_name,

        "Molecular Formula":
            rdMolDescriptors.CalcMolFormula(mol),

        "Exact Mass":
            round(
                rdMolDescriptors.CalcExactMolWt(mol),
                4
            ),

        "Molecular Weight":
            round(
                Descriptors.MolWt(mol),
                4
            ),

        "LogP":
            round(
                Crippen.MolLogP(mol),
                3
            ),

        "TPSA":
            round(
                rdMolDescriptors.CalcTPSA(mol),
                2
            ),

        "Heavy Atoms":
            rdMolDescriptors.CalcNumHeavyAtoms(mol),

        "H-Bond Donors":
            rdMolDescriptors.CalcNumHBD(mol),

        "H-Bond Acceptors":
            rdMolDescriptors.CalcNumHBA(mol),

        "Rotatable Bonds":
            rdMolDescriptors.CalcNumRotatableBonds(mol),

        "Ring Count":
            rdMolDescriptors.CalcNumRings(mol),

        "Fraction Csp3":
            round(
                rdMolDescriptors.CalcFractionCSP3(mol),
                3
            ),

    }

    properties_df = pd.DataFrame([properties])

    # ------------------------------------------------------
    # Functional Group Scan
    # ------------------------------------------------------

    functional_groups = {

        "Amide":
            "C(=O)N",

        "Alcohol":
            "[OX2H]",

        "Ether":
            "COC",

        "Ester":
            "C(=O)O",

        "Carboxylic Acid":
            "C(=O)[OH]",

        "Primary Amine":
            "[NH2]",

        "Secondary Amine":
            "[NH]",

        "Tertiary Amine":
            "[NX3]([#6])([#6])[#6]",

        "Pyridine Ring":
            "n1ccccc1",

        "Phenyl Ring":
            "c1ccccc1",

        "Halogen":
            "[F,Cl,Br,I]",

        "Acid Sensitive Amide":
            "[C:1](=O)[N:2]"

    }

    fg_results = []

    for fg_name, smarts in functional_groups.items():

        patt = Chem.MolFromSmarts(smarts)

        if patt is None:
            continue

        matches = mol.GetSubstructMatches(patt)

        fg_results.append({

            "Functional Group": fg_name,

            "SMARTS": smarts,

            "Count": len(matches),

            "Possible Risk":
                "Yes" if len(matches) else "No"

        })

    fg_df = pd.DataFrame(fg_results)

    # ------------------------------------------------------
    # Degradation Prediction
    # ------------------------------------------------------

    reaction_smarts = {

        "Amide Hydrolysis":
            "[C:1](=O)[N:2]>>[C:1](=O)O.[N:2]",

        "Alcohol Oxidation":
            "[C:1][OH:2]>>[C:1]=O",

        "Ether Cleavage":
            "[C:1]O[C:2]>>[C:1]O.[C:2]O"

    }

    predicted_products = []

    for reaction_name, rxn_smarts in reaction_smarts.items():

        rxn = AllChem.ReactionFromSmarts(rxn_smarts)

        if rxn is None:
            continue

        try:

            product_sets = rxn.RunReactants((mol,))

        except Exception:
            continue

        for product_set in product_sets:

            for product in product_set:

                try:

                    Chem.SanitizeMol(product)

                    predicted_products.append({

                        "Parent":

                            api_name,

                        "Reaction":

                            reaction_name,

                        "Predicted Product":

                            Chem.MolToSmiles(product),

                        "Formula":

                            rdMolDescriptors.CalcMolFormula(product),

                        "Exact Mass":

                            round(
                                rdMolDescriptors.CalcExactMolWt(product),
                                4
                            )

                    })

                except Exception:
                    continue

    products_df = pd.DataFrame(predicted_products)

    if not products_df.empty:

        products_df = products_df.drop_duplicates(
            subset=["Predicted Product"]
        )

    # ------------------------------------------------------
    # Return Payload
    # ------------------------------------------------------

    return {

        "image": structure_svg,

        "properties": properties_df,

        "functional_groups": fg_df,

        "degradants": products_df,

        "molecule": mol,

        "smiles": Chem.MolToSmiles(mol),

        "inchi":

            Chem.MolToInchi(mol),

        "inchikey":

            Chem.MolToInchiKey(mol)

    }