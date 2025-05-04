# Processes the abstracts in a form amendable for RAG
from pathlib import Path

import jsonlines
from diskcache import Cache
from utils import get_issns, get_journals_by_issn, parse_hive_cache_key

proj_dir = Path(__file__).parents[2]
cache = Cache(proj_dir / "data" / "cache")


def parse_crossref_cache_entry(entry: dict, journal: str) -> list[dict]:
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
            {
                "title": title,
                "year": year,
                "authors": authors,
                "abstract": abstract,
                "journal": journal,
            }
        )

    return results


if __name__ == "__main__":
    jsonl_file = proj_dir / "data" / "abstracts.jsonl"
    if jsonl_file.exists():
        jsonl_file.unlink()
    assert not jsonl_file.exists()
    print(jsonl_file)
    keys = list(cache)
    issns = get_issns()
    issns_inv = get_journals_by_issn()

    dfs = []
    for k in keys:
        # Figure out journal
        data = parse_hive_cache_key(k)
        journal = issns_inv[data["issn"]]
        v = cache[k]

        vp = parse_crossref_cache_entry(v, journal)

        with jsonlines.open(jsonl_file, mode="a") as writer:
            writer.write_all(vp)

    assert jsonl_file.exists(), "File does not exist"
