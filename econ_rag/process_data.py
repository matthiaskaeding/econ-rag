# Processes the abstracts in a form amendable for RAG
from pathlib import Path
from pprint import pprint

from diskcache import Cache
from utils import get_issns

proj_dir = Path(__file__).parents[1]
cache = Cache(proj_dir / "data" / "cache")


def parse_crossref_cache_entry(entry: dict, issns) -> list[dict]:
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


if __name__ == "__main__":
    keys = list(cache)
    issns = get_issns()
    k = keys[0]
    entry = cache[k]
    pprint(entry)
