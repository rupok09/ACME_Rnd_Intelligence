import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus


def clean_text(text):
    if text is None:
        return ""
    return " ".join(str(text).split())


def search_dailymed_labels(query):
    url = (
        "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
        f"?drug_name={quote_plus(query)}"
    )

    try:
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            return []

        data = response.json()
        labels = data.get("data", [])

        results = []

        for item in labels[:10]:
            setid = item.get("setid")
            title = item.get("title", "Unknown label")

            if setid:
                results.append(
                    {
                        "title": title,
                        "setid": setid,
                        "label_link": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}",
                        "pdf_link": f"https://dailymed.nlm.nih.gov/dailymed/downloadpdffile.cfm?setId={setid}",
                    }
                )

        return results

    except Exception as error:
        print("DailyMed search error:", error)
        return []


def get_dailymed_xml(setid):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code != 200:
            return ""

        return response.text

    except Exception as error:
        print("DailyMed XML error:", error)
        return ""


def tag_name(element):
    return element.tag.split("}")[-1].lower()


def get_table_rows(table):
    rows = []

    for tr in table.iter():
        if tag_name(tr) != "tr":
            continue

        cells = []

        for cell in tr:
            if tag_name(cell) in ["td", "th"]:
                text = clean_text(" ".join(cell.itertext()))
                if text:
                    cells.append(text)

        if cells:
            rows.append(cells)

    return rows


def find_table_by_title(root, title_keyword):
    for table in root.iter():
        if tag_name(table) != "table":
            continue

        table_text = clean_text(" ".join(table.itertext())).lower()

        if title_keyword.lower() in table_text:
            return table

    return None


def extract_inactive_ingredients_from_xml(root):
    table = find_table_by_title(root, "inactive ingredients")

    if table is None:
        return []

    rows = get_table_rows(table)
    data = []

    for row in rows:
        joined = " ".join(row).lower()

        if "inactive ingredients" in joined:
            continue
        if "ingredient name" in joined:
            continue
        if "strength" in joined and len(row) <= 2:
            continue

        ingredient = row[0].strip() if len(row) >= 1 else ""
        strength = row[1].strip() if len(row) >= 2 else "—"

        if ingredient:
            data.append(
                {
                    "Ingredient Name": ingredient,
                    "Strength": strength if strength else "—",
                }
            )

    return data


def extract_product_characteristics_from_xml(root):
    table = find_table_by_title(root, "product characteristics")

    if table is None:
        return []

    rows = get_table_rows(table)

    valid_keys = [
        "color",
        "shape",
        "score",
        "size",
        "imprint code",
        "flavor",
        "contains",
    ]

    data = []

    for row in rows:
        for i in range(0, len(row) - 1, 2):
            key = row[i].strip()
            value = row[i + 1].strip()

            if key.lower() in valid_keys and value:
                data.append(
                    {
                        "Characteristic": key,
                        "Value": value,
                    }
                )

    return data


def extract_dailymed_label_tables(setid):
    xml_text = get_dailymed_xml(setid)

    if not xml_text:
        return [], []

    try:
        root = ET.fromstring(xml_text)

        inactive_ingredients = extract_inactive_ingredients_from_xml(root)
        product_characteristics = extract_product_characteristics_from_xml(root)

        return inactive_ingredients, product_characteristics

    except Exception as error:
        print("DailyMed XML parse error:", error)
        return [], []