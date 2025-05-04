# Try transformers for embeddings
# %%
from pathlib import Path
from pprint import pprint as print

import polars as pl
from rank_bm25 import BM25Okapi

from app.data_prep.clean_data import clean_text

proj_dir = Path(__file__).parents[2]


data_file = proj_dir / "data" / "abstracts_clean.parquet"

if __name__ == "__main__":
    df = pl.read_parquet(data_file)
    print(df)
    corpus = df.get_column("tokenized_abstract").to_list()
    bm25 = BM25Okapi(corpus)

    query = "Randomized controlled trial"

    tokenized_query = clean_text(query)
    doc_scores = bm25.get_scores(tokenized_query)

    n = 3
    topn = bm25.get_top_n(tokenized_query, corpus, n=n)
    print(topn)  # Seems really bad
