# Gets the abstract and other information of articles in top 5
# Stores results in cache
from datetime import date
from os import getenv
from pathlib import Path
from typing import Dict, List

import requests
from diskcache import Cache
from dotenv import load_dotenv
from tqdm import tqdm
from utils import get_issns, make_hive_cache_key

proj_dir = Path(__file__).parents[2]
cache = Cache(proj_dir / "data" / "cache")

load_dotenv()
user_email = getenv("USER_EMAIL")


def fetch_crossref_metadata(
    date_from: str,
    date_to: str,
    issn: str,
    cache: Cache,
    user_email: str,
    prefix: str = None,
    verbose=False,
) -> List[Dict]:
    """
    Fetch metadata from Crossref API for a journal in a date range,
    including the journal title (container-title).
    """
    base_url = "https://api.crossref.org/works"
    headers = {"User-Agent": f"MyCrossrefClient/1.0 (mailto:{user_email})"}

    # Filters
    common = [
        "type:journal-article",
        f"from-pub-date:{date_from}",
        f"until-pub-date:{date_to}",
        "has-abstract:true",
    ]
    if prefix:
        key_filter = f"prefix:{prefix}"
    elif issn:
        key_filter = f"issn:{issn}"
    else:
        raise ValueError("You must supply either an ISSN or a DOI prefix")
    filters = [key_filter] + common

    params = {
        "filter": ",".join(filters),
        "rows": 1000,
        "select": "DOI,title,author,issued,abstract,container-title",
        "sort": "published",
        "order": "desc",
        "mailto": user_email,
        "cursor": "*",
    }

    all_items = []
    while True:
        cache_key = make_hive_cache_key(
            issn=issn,
            date_from=date_from,
            date_to=date_to,
            cursor=params["cursor"],
            prefix=prefix,
        )
        if cache_key in cache:
            data = cache[cache_key]
        else:
            resp = requests.get(base_url, headers=headers, params=params)
            resp.raise_for_status()
            if verbose:
                print("REQUEST ▶", resp.url)
                print("STATUS  ▶", resp.status_code)
                print("HEADERS ▶", resp.headers.get("Retry-After", "none"))
                print("BODY    ▶", resp.text[:200], "…")
            data = resp.json()["message"]
            cache[cache_key] = data

        items = data.get("items", [])
        all_items.extend(items)

        if len(items) < params["rows"]:
            break

        params["cursor"] = data["next-cursor"]

    return all_items


def generate_yearly_date_ranges(start_year: int) -> list[dict]:
    """
    Generate a list of yearly date ranges from start_year to current year.

    Returns:
        List[Dict]: Each dict has 'year', 'date_from', 'date_to'
    """
    today = date.today()
    current_year = today.year

    ranges = []
    for year in range(start_year, current_year + 1):
        date_from = f"{year}-01-01"
        if year == current_year:
            date_to = today.isoformat()
        else:
            date_to = f"{year}-12-31"
        ranges.append({"year": year, "date_from": date_from, "date_to": date_to})

    return ranges


if __name__ == "__main__":
    START_YEAR = 2000
    date_ranges = generate_yearly_date_ranges(START_YEAR)
    issns = get_issns()
    DOI_PREFIX = {
        # "American Economic Review": "10.1257/aer",
        "Journal of Political Economy": "10.1086",  # JPE
    }

    for date_range in tqdm(date_ranges):
        for journal in issns:
            prefix = DOI_PREFIX.get(journal)
            print_issn = issns[journal]["print"]
            online_issn = issns[journal]["online"]
            date_range["journal"] = journal
            items_print = fetch_crossref_metadata(
                date_from=date_range["date_from"],
                date_to=date_range["date_to"],
                issn=print_issn,
                cache=cache,
                user_email=user_email,
                prefix=prefix,
            )
            if not items_print:
                msg = f"No print items for {journal} in {date_range}"
                print(msg)
            items_online = fetch_crossref_metadata(
                date_from=date_range["date_from"],
                date_to=date_range["date_to"],
                issn=online_issn,
                cache=cache,
                user_email=user_email,
                prefix=prefix,
            )
            if not items_online:
                msg = f"No online items for {journal} in {date_range}"
                print(msg)

    print("Got raw abstracts")
