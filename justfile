# Format and fix errors in code via ruff
lint:
    uv tool run ruff format 
    uv tool run ruff check --fix

# Gets the data from top 5 via crossref
get-abstracts:
    uv run app/data_prep/get_data.py

# Process  and cleans the data, stores a parquet file
process-data:
    uv run app/data_prep/process_data.py

# Store embeddings
save-embeddings:
    uv run python app/data_prep/save_embeddings.py

# All data commands
data: get-abstracts process-data

# Runs tests
test:
    uv run pytest tests

# Strip notebooks of metadata
strip-nbs:
    uv tool run nbstripout --keep-output experiments/explore_data.ipynb