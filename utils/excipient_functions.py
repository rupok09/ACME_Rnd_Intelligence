EXCIPIENT_FUNCTIONS = {
    "microcrystalline cellulose": "Diluent / Dry binder",
    "mcc": "Diluent / Dry binder",
    "lactose": "Diluent",
    "mannitol": "Diluent",
    "starch": "Diluent / Disintegrant",
    "hydroxypropyl cellulose": "Binder",
    "hpc": "Binder",
    "povidone": "Binder",
    "pvp": "Binder",
    "croscarmellose sodium": "Superdisintegrant",
    "ccs": "Superdisintegrant",
    "crospovidone": "Superdisintegrant",
    "sodium starch glycolate": "Superdisintegrant",
    "magnesium stearate": "Lubricant",
    "stearic acid": "Lubricant",
    "colloidal silicon dioxide": "Glidant",
    "silicon dioxide": "Glidant",
    "talc": "Glidant / Anti-adherent",
    "hypromellose": "Film coating polymer",
    "hpmc": "Film coating polymer",
    "polyethylene glycol": "Plasticizer",
    "peg 400": "Plasticizer",
    "titanium dioxide": "Opacifier",
    "ferric oxide red": "Colorant",
    "iron oxide": "Colorant",
    "hydrogenated castor oil": "Lubricant / Hydrophobic excipient",
}


def get_excipient_function(excipient_name):
    name = excipient_name.lower()

    for key, function in EXCIPIENT_FUNCTIONS.items():
        if key in name:
            return function

    return "Review manually"