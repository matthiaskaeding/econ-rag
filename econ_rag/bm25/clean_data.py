# Processes the abstracts in a form amendable for RAG
import re
from pathlib import Path

import jsonlines
import nltk
import polars as pl
from diskcache import Cache
from nltk.tokenize import word_tokenize

proj_dir = Path(__file__).parents[2]
cache = Cache(proj_dir / "data" / "cache")
jsonl_file = proj_dir / "data" / "abstracts.jsonl"


def clean_text(text: str) -> str:
    """Cleans text -> lowers and tokenizes. Needs downloaded corpus"""

    assert isinstance(text, str)

    text = text.lower()
    clean_text = re.sub(r"<[^>]+>", "", text)
    tokens = word_tokenize(clean_text)
    if not tokens:
        return ""

    if tokens[0] == "Abstract":
        start = 1
    else:
        start = 0

    return " ".join(tokens[start:])


if __name__ == "__main__":
    nltk.download("punkt")
    entries = []
    with jsonlines.open(jsonl_file) as reader:
        for obj in reader:
            entries.append(obj)
    df = (
        pl.DataFrame(entries)
        .sort("journal", "year")
        .filter(pl.col("authors").list.len() > 0, pl.col("abstract") != "")
    )
    df = df.with_columns(
        pl.col("abstract").map_elements(clean_text).alias("tokenized_abstract")
    )
    print(df.head())
    df.write_parquet(proj_dir / "data" / "abstracts_clean.parquet")
