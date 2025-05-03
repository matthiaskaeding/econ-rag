# Format and fix errors in code via ruff
lint:
    uv tool run ruff format 
    uv tool run ruff check --fix

# Gets the data from top 5 via crossref
get-abstracts:
    uv run econ_rag/data/get_data.py

# Process the data into RAG-able form
process-data:
    uv run econ_rag/data/process_data.py

# Cleans the data, deleting empy abstrats etc. and applies tokenizer as prep for bm25
clean-data-bm25:
    uv run python econ_rag/bm25/clean_data.py 

# Runs tests
test:
    uv run pytest tests
