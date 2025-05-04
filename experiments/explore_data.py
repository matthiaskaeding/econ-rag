# %%
from pathlib import Path
from pprint import pprint
import plotnine as pn
import polars as pl
from plotnine import aes, ggplot, labs

pl.Config.set_tbl_rows(20)
pn.theme_set(pn.theme_matplotlib())

# %%
proj_dir = Path(__file__).parents[1]
print(proj_dir)
file = proj_dir / "data" / "abstracts_clean.parquet"
assert file.exists()
df = pl.read_parquet(file)
df.glimpse()

# %%
df.group_by("journal").len()

# %%
counts = df.group_by("journal", "year").len()
(
    ggplot(counts)
    + aes("year", "len", color="journal")
    + pn.geom_line()
    + labs(y="Number of abstracts")
)

# %%
x = (
    df.filter(pl.col("abstract").str.to_lowercase().str.contains("elasticity"))
    .get_column("abstract")
    .sample(1)
    .item()
)
pprint(x)

# %%
