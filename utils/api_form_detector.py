def guess_parent_form(api_name):
    salt_terms = [
        "hydrochloride", "hcl", "sodium", "potassium", "calcium",
        "magnesium", "phosphate", "sulfate", "mesylate", "besylate",
        "tartrate", "citrate", "maleate", "fumarate", "succinate",
        "dihydrate", "hydrate", "monohydrate", "anhydrous"
    ]

    words = api_name.split()
    parent_words = [
        word for word in words
        if word.lower().replace(".", "") not in salt_terms
    ]

    parent = " ".join(parent_words).strip()

    if parent == "":
        return api_name

    return parent


def detect_api_forms(api_name):
    parent = guess_parent_form(api_name)

    forms = [
        {
            "label": api_name,
            "type": "Exact input form",
            "search_name": api_name
        }
    ]

    if parent.lower() != api_name.lower():
        forms.append(
            {
                "label": parent,
                "type": "Parent compound / free base",
                "search_name": parent
            }
        )

    return forms