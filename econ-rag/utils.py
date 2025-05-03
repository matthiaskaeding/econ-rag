def make_hive_cache_key(**kwargs) -> str:
    """
    Construct a Hive-style cache key from keyword arguments in Hive-style format.
    Example: "issn=0033-5533/date_from=2020-01-01/date_to=2020-12-31/offset=0"
    """
    return "/".join(f"{key}={value}" for key, value in sorted(kwargs.items()))


def parse_crossref_cache_entry(entry: dict) -> list[dict]:
    """
    Extracts metadata from a single Crossref API response stored in diskcache.

    Args:
        entry (dict): The cached Crossref API response.

    Returns:
        List[Dict]: List of simplified paper metadata dictionaries.
    """
    if not isinstance(entry, dict):
        raise ValueError("Cache entry must be a dictionary.")

    items = entry.get("message", {}).get("items", [])
    results = []

    for item in items:
        title = item.get("title", [""])[0]
        year = item.get("issued", {}).get("date-parts", [[None]])[0][0]
        authors = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in item.get("author", [])
        ]
        abstract = item.get("abstract", "")
        results.append(
            {"title": title, "year": year, "authors": authors, "abstract": abstract}
        )

    return results


def get_issns() -> dict:
    """Returns dict of issns for top 5"""
    # issn
    return {
        "Quarterly Journal of Economics": {
            "print_issn": "0033-5533",
            "online_issn": "1531-4650",
        },
        "American Economic Review": {
            "print_issn": "0002-8282",
            "online_issn": "1944-7981",
        },
        "Journal of Political Economy": {
            "print_issn": "0022-3808",
            "online_issn": "1537-534X",
        },
        "Econometrica": {"print_issn": "0012-9682", "online_issn": "1468-0262"},
        "Review of Economic Studies": {
            "print_issn": "0034-6527",
            "online_issn": "1467-937X",
        },
    }
