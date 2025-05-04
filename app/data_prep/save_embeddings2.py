# Computes and saves embeddings in data/
# %%
from pathlib import Path
from typing import List
import polars as pl
import torch
from diskcache import Cache
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from adapters import AutoAdapterModel
import numpy as np
from tqdm import tqdm

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


model_name = "allenai/specter2"


class SpecterEmbeddings:
    def __init__(self, batch_size: int = 32):
        # load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")
        self.model = AutoAdapterModel.from_pretrained("allenai/specter2_base")
        self.batch_size = batch_size

        self.model.load_adapter(
            "allenai/specter2", source="hf", load_as="specter2", set_active=True
        )

    def embed(self, text_batch: List[str]) -> np.array:
        all_embeddings = []
        for i in tqdm(
            range(0, len(text_batch), self.batch_size), desc="Processing batches"
        ):
            batch = text_batch[i : i + self.batch_size]
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                return_tensors="pt",
                return_token_type_ids=False,
                max_length=512,
            )
            output = self.model(**inputs)
            embeddings = output.last_hidden_state[:, 0, :]
            all_embeddings.append(embeddings.detach().numpy())

        return np.vstack(all_embeddings)


specter_embeddings = SpecterEmbeddings(6)
# %%
print("Building embeddings")
abstracts = df.get_column("abstract").to_list()
embeddings = specter_embeddings.embed(abstracts)
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
df.write_parquet(
    proj_dir / "data" / f"embeddings_{model_name.lower().replace('/', '_')}.parquet"
)
