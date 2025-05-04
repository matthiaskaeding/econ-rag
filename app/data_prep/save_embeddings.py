# Computes and saves embeddings in data/
# %%
from pathlib import Path

import polars as pl
import torch
from diskcache import Cache
from sentence_transformers import SentenceTransformer

proj_dir = Path(__file__).parents[2]
cache = Cache(proj_dir / "data" / "cache")
parq_file = proj_dir / "data" / "abstracts_clean.parquet"
df = pl.read_parquet(parq_file)
print(df)
# %%
device = (
    torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
)
print(f"Using device: {device}")
# %%
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
# %%
print("Building embeddings")
abstracts = df.get_column("abstract").to_list()
embeddings = model.encode(abstracts, convert_to_tensor=False, show_progress_bar=True)
print(embeddings)
# %%
print(embeddings.shape)
# %%
# Make dataframe and write to disk
emb_df = pl.DataFrame(embeddings).rename(lambda x: x.replace("column", "emb"))
df = df.hstack(emb_df)

# %%
df.write_parquet(proj_dir / "data" / "embeddings.parquet")
