import pandas as pd


def html_link(label, url):
    if not url:
        return "—"

    return f'<a href="{url}" target="_blank">{label}</a>'


def normalize_value(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() == "none":
        return None

    return value


def merge_property_values(collected_sources):
    valid_items = []

    for item in collected_sources:
        value = normalize_value(item.get("value"))

        if value:
            valid_items.append({
                "value": value,
                "source": item.get("source"),
                "link": item.get("link")
            })

    if not valid_items:
        return {
            "value": "Not Found",
            "status": "❌ Missing",
            "sources": "—",
            "references": "—"
        }

    unique_values = list(dict.fromkeys([item["value"] for item in valid_items]))
    unique_sources = list(dict.fromkeys([item["source"] for item in valid_items]))

    unique_links = []
    seen_link_labels = set()

    for item in valid_items:
        label = item.get("source")
        link = item.get("link")

        key = f"{label}-{link}"

        if link and key not in seen_link_labels:
            unique_links.append(html_link(label, link))
            seen_link_labels.add(key)

    if len(unique_values) == 1:
        final_value = unique_values[0]
        status = "✅ Found"
    else:
        final_value = " / ".join(unique_values)
        status = "⚠ Review"

    return {
        "value": final_value,
        "status": status,
        "sources": ", ".join(unique_sources),
        "references": " · ".join(unique_links) if unique_links else "—"
    }


def build_result_table(selected_properties, property_category_map, selected_records):
    rows = []

    for property_name in selected_properties:
        category = property_category_map.get(property_name, "Other")
        collected_sources = []

        for record in selected_records:
            source_data = record.get("data", {})

            if property_name in source_data:
                collected_sources.append(source_data[property_name])

        merged = merge_property_values(collected_sources)

        rows.append({
            "Category": category,
            "Property": property_name,
            "Value": merged["value"],
            "Status": merged["status"],
            "Source(s)": merged["sources"],
            "Reference(s)": merged["references"]
        })

    return pd.DataFrame(rows)