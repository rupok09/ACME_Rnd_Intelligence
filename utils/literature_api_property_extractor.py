import re
import pandas as pd
import fitz


API_PROPERTY_KEYWORDS = {
    "Physical Description": [
        "physical description", "description", "appearance", "white powder",
        "crystalline powder", "color", "odour", "odor"
    ],
    "Melting Point": [
        "melting point", "m.p.", "mp", "melting range"
    ],
    "Solubility": [
        "solubility", "soluble", "freely soluble", "sparingly soluble",
        "slightly soluble", "practically insoluble", "insoluble"
    ],
    "Solubility vs pH": [
        "ph dependent solubility", "solubility at ph", "solubility in buffer",
        "ph solubility", "ph-solubility"
    ],
    "pKa": [
        "pka", "dissociation constant", "ionization constant"
    ],
    "LogP / LogD": [
        "logp", "log p", "logd", "log d", "partition coefficient",
        "distribution coefficient"
    ],
    "BCS Classification": [
        "bcs class", "biopharmaceutics classification", "class ii",
        "class i", "class iii", "class iv"
    ],
    "Solid-state Form / Polymorph": [
        "polymorph", "polymorphic form", "crystalline form",
        "form i", "form ii", "form iii", "amorphous", "crystal form"
    ],
    "Bulk Density": [
        "bulk density", "loose bulk density"
    ],
    "Tapped Density": [
        "tapped density"
    ],
    "Flowability": [
        "flowability", "angle of repose", "carr index", "hausner ratio",
        "flow property", "powder flow"
    ],
    "Hygroscopicity": [
        "hygroscopic", "hygroscopicity", "moisture uptake",
        "water uptake", "moisture sorption"
    ],
    "Photostability": [
        "photostability", "photo stability", "light stability",
        "light exposure", "photodegradation"
    ],
    "Chemical Stability - Solution": [
        "solution stability", "stable in solution", "aqueous stability",
        "degradation in solution"
    ],
    "Chemical Stability - Solid State": [
        "solid state stability", "solid-state stability", "stable in solid state",
        "solid degradation"
    ],
    "Forced Degradation Data": [
        "forced degradation", "stress degradation", "acid degradation",
        "base degradation", "alkaline degradation", "oxidative degradation",
        "thermal degradation", "photolytic degradation"
    ]
}


def clean_text(value):
    if value is None:
        return ""
    return " ".join(str(value).replace("\n", " ").split()).strip()


def extract_text_by_page(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    pages = []

    for page_no, page in enumerate(doc, start=1):
        pages.append(
            {
                "Document": uploaded_file.name,
                "Page": page_no,
                "Text": page.get_text("text"),
            }
        )

    doc.close()
    return pages


def split_into_sentences(text):
    text = clean_text(text)

    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9])",
        text
    )

    clean_sentences = []

    for sentence in sentences:
        sentence = clean_text(sentence)

        if len(sentence) >= 25:
            clean_sentences.append(sentence)

    return clean_sentences


def get_context_sentence(sentences, index):
    previous_sentence = sentences[index - 1] if index > 0 else ""
    current_sentence = sentences[index]
    next_sentence = sentences[index + 1] if index < len(sentences) - 1 else ""

    context = " ".join(
        [
            previous_sentence,
            current_sentence,
            next_sentence,
        ]
    )

    return clean_text(context)


def extract_api_properties_from_pdf(uploaded_files):
    results = []

    for uploaded_file in uploaded_files:
        pages = extract_text_by_page(uploaded_file)

        for page in pages:
            sentences = split_into_sentences(page["Text"])

            for index, sentence in enumerate(sentences):
                lower_sentence = sentence.lower()

                for property_name, keywords in API_PROPERTY_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword.lower() in lower_sentence:
                            evidence = get_context_sentence(sentences, index)

                            results.append(
                                {
                                    "Document": uploaded_file.name,
                                    "Page": page["Page"],
                                    "Property": property_name,
                                    "Extracted Value / Evidence": evidence,
                                }
                            )
                            break

    if not results:
        return pd.DataFrame(
            columns=[
                "Document",
                "Page",
                "Property",
                "Extracted Value / Evidence",
            ]
        )

    df = pd.DataFrame(results).drop_duplicates()

    df = df.sort_values(
        by=["Document", "Page", "Property"],
        ascending=True
    ).reset_index(drop=True)

    return df