# Format and fix errors in code via ruff
lint:
    uv tool run ruff format 
    uv tool run ruff check --fix

# Gets the data from top 5 via crossref
get-abstracts:
    uv run econ-rag/get_data.py
