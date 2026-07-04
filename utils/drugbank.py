from urllib.parse import quote_plus


def search_drugbank_records(api_name):
    return [
        {
            "source": "DrugBank",
            "record_name": api_name,
            "record_id": "Search only",
            "formula": "—",
            "molecular_weight": "—",
            "structure_url": "",
            "link": f"https://go.drugbank.com/unearth/q?searcher=drugs&query={quote_plus(api_name)}",
            "search_name": api_name,
            "data": {}
        }
    ]