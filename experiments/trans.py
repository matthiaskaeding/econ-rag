# Try transformers for embeddings
# Works okay
# %%
from pathlib import Path
from pprint import pprint as print

import numpy as np
import polars as pl
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# %%
device = (
    torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
)
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
# %%
proj_dir = Path(__file__).parents[1]
data_file = proj_dir / "data" / "embeddings.parquet"
assert data_file.exists()
df = pl.read_parquet(data_file)
assert "embedding" in df.columns
print(df)
# %%
embeddings = np.vstack(df["embedding"].to_list()).astype("float32")
print(embeddings.shape)
# %%
abstracts = df["abstract"].to_list()
query = "Papers which estimate elasticities"
q_emb = model.encode([query], convert_to_numpy=True)
# %%
print(f"{query=}")
sims = cosine_similarity(q_emb, embeddings)[0]
top_k = 5
top_idx = sims.argsort()[::-1][:top_k]
print("5 closest queries")
for rank, idx in enumerate(top_idx, start=1):
    print(f"{rank}. Score: {sims[idx]:.4f}\n   Abstract: {abstracts[idx]}\n")

# %%
