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
model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name, device=device)
# %%
print("Building embeddings")
abstracts = df.get_column("abstract").to_list()
embeddings = model.encode(abstracts, convert_to_tensor=False, show_progress_bar=True)
print(embeddings.shape)
print(embeddings)
# %%
emb_series = pl.Series(
    name="embedding",
    values=embeddings.tolist(),
    dtype=pl.Array(pl.Float32, embeddings.shape[1]),
)
df = df.with_columns(emb_series)
# %%
print("df with embeddings:", df)
# %%
df.write_parquet(proj_dir / "data" / f"embeddings_{model_name.lower()}.parquet")
