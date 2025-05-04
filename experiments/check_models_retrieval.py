# Try several model for retrieval
# %%
from pathlib import Path
from pprint import pprint as print

import numpy as np
import polars as pl
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sys import path

path.append("../app")
from data_prep.save_embeddings2 import SpecterEmbeddings

# %%
device = (
    torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
)
model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name, device=device)
# %%
proj_dir = Path(__file__).parents[1]

data_file = proj_dir / "data" / f"embeddings_{model_name}.parquet"
print(data_file)
assert data_file.exists()
df = pl.read_parquet(data_file)
assert "embedding" in df.columns
print(df)
# %%


def print_abstracts(df):
    for a in df["abstract"]:
        print(a)


def find_topk(df, query, model, k=10, verbose=True):
    """Simple function to get top 5 queries"""
    abstracts = df["abstract"].to_list()
    embeddings = np.vstack(df["embedding"].to_list()).astype("float32")
    try:
        q_emb = model.encode([query], convert_to_numpy=True)
    except AttributeError:
        q_emb = model.embed([query])
    sims = cosine_similarity(q_emb, embeddings)[0]
    top_idx = sims.argsort()[::-1][:k]

    qrs = []
    print(f"{k} closest queries")
    for rank, idx in enumerate(top_idx, start=1):
        row = (rank, sims[idx], abstracts[idx])
        qrs.append(row)

    matches = pl.DataFrame(qrs, schema=("rank", "distance", "abstract"))
    if verbose:
        print_abstracts(matches)

    return matches


query = "What are reasonable values for demand elasticities? I need numbers"
find_topk(df, query, model)
# %%
specter_model = SpecterEmbeddings(6)
# %%
model_name = specter_model.name
file = proj_dir / "data" / f"embeddings_{model_name.replace('/', '-')}.parquet"
assert file.exists(), f"{file} not there"
df_allen = pl.read_parquet(file)
# %%
find_topk(df_allen, query, specter_model)
# %%
