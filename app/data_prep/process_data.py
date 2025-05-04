# Processes the abstracts in a form amendable for RAG
import re
from pathlib import Path

import nltk
import polars as pl
from diskcache import Cache
from app.data_prep.utils import get_issns, get_journals_by_issn, parse_hive_cache_key

from nltk.tokenize import word_tokenize

proj_dir = Path(__file__).parents[2]
cache = Cache(proj_dir / "data" / "cache")


def parse_crossref_cache_entry(entry: dict, journal: str = None) -> list[dict]:
    """
    Extracts metadata from a Crossref "message" dict (e.g. what you store in diskcache).

    Args:
        entry (dict): The cached Crossref `message` dict (already entry["message"], not the full response).
        journal (str, optional): Fallback journal name if container-title is missing.

    Returns:
        List[Dict]: List of simplified paper metadata dicts, including journal title.
    """
    if not isinstance(entry, dict):
        raise ValueError("Cache entry must be a dictionary.")

    # Now entry is the `message` object itself
    items = entry.get("items", [])

    results = []
    for item in items:
        doi = (item.get("DOI") or [""])[0]
        title = (item.get("title") or [""])[0]
        year = (item.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0]
        authors = [
            " ".join(filter(None, (a.get("given"), a.get("family"))))
            for a in item.get("author", [])
        ]
        abstract = item.get("abstract", "")
        # container-title is a list: pick first element if present
        journal_name = (item.get("container-title") or [None])[0] or ""

        results.append(
            {
                "title": title,
                "year": year,
                "doi": doi,
                "authors": authors,
                "abstract": abstract,
                "journal": journal_name,
                "desired_journal": journal,
            }
        )

    return results


def clean_text(text: str, remove_abstract=False) -> str:
    """Cleans text -> lowers and tokenizes. Needs downloaded corpus"""

    assert isinstance(text, str)

    text = text.lower()
    clean_text = re.sub(r"<[^>]+>", "", text)
    tokens = word_tokenize(clean_text)
    if not tokens:
        return ""

    if remove_abstract:
        if tokens[0] == "abstract":
            start = 1
        elif tokens[0].startswith("abstract"):
            tokens[0] = tokens[0].replace("abstract", "")
            start = 0
        else:
            start = 0
    else:
        start = 0

    return " ".join(tokens[start:])


if __name__ == "__main__":
    nltk.download("punkt")
    keys = list(cache)
    issns = get_issns()
    issns_inv = get_journals_by_issn()

    dfs = []
    for k in keys:
        # Figure out journal
        print(k)
        data = parse_hive_cache_key(k)
        journal = issns_inv[data["issn"]]
        v = cache[k]
        vp = parse_crossref_cache_entry(v, journal)

        tmp = pl.DataFrame(vp)
        if not tmp.is_empty():
            dfs.append(tmp)

    df = pl.concat(dfs)
    df = df.sort("journal", "year").filter(
        pl.col("authors").list.len() > 0, pl.col("abstract") != ""
    )

    df = df.with_columns(
        pl.col("abstract").alias("abstract_original"),
        pl.col("abstract")
        .str.replace_all(r"<[^>]+>", "")
        .str.strip_chars()
        .str.replace(r"^\s*Abstract\b", "")
        .str.replace(r"^\s*Abstract", "")
        .str.replace(r"^\s*ABSTRACT\b", ""),
    )
    df = df.with_columns(
        pl.col("abstract")
        .map_elements(lambda x: clean_text(x, True), return_dtype=str)
        .alias("tokenized_abstract"),
        pl.col("journal")
        .replace("The Review of Economic Studies", "Review of Economic Studies")
        .alias("journal"),
    ).with_columns(pl.format("{}\n{}", "title", "abstract").alias("abstract"))
    df = df.unique(subset=["abstract"])
    counts = df.group_by("journal", "desired_journal").len()
    print("Counts by journal", counts)
    with pl.Config(tbl_cols=20):
        print("Data", df.head())
    df.write_parquet(proj_dir / "data" / "abstracts_clean.parquet")
