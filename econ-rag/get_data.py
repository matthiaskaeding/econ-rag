# Gets the abstract and other information of articles in top 5
# Stores results in cache
from datetime import date
import requests
from diskcache import Cache
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from pprint import pprint
from utils import make_hive_cache_key, get_issns

proj_dir = Path(__file__).parents[1]
cache = Cache(proj_dir / "data" / "cache")

load_dotenv()
user_email = getenv("USER_EMAIL")


def fetch_crossref_metadata(
    date_from: str, date_to: str, issn: str, cache: Cache, user_email: str
) -> List[Dict]:
    """
    Fetch metadata from Crossref API for a journal in a date range using Hive-style cache keys.

    Args:
        date_from (str): Start date in 'YYYY-MM-DD'.
        date_to (str): End date in 'YYYY-MM-DD'.
        issn (str): Journal ISSN.
        cache (Cache): DiskCache instance.
        user_email (str): Email for polite API access.

    Returns:
        List[Dict]: List of article metadata.
    """
    base_url = f"https://api.crossref.org/journals/{issn}/works"
    headers = {"User-Agent": f"MyCrossrefClient/1.0 (mailto:{user_email})"}

    params = {
        "filter": f"type:journal-article,from-pub-date:{date_from},until-pub-date:{date_to}",
        "rows": 1000,
        "select": "title,author,issued,abstract",
        "sort": "published",
        "order": "desc",
        "mailto": user_email,
    }

    offset = 0
    n_results = 0

    while True:
        params["offset"] = offset
        cache_key = make_hive_cache_key(
            issn=issn, date_from=date_from, date_to=date_to, offset=offset
        )

        if cache_key in cache:
            response_data = cache[cache_key]
        else:
            response = requests.get(base_url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Error {response.status_code}: {response.text}")
                break
            response_data = response.json()
            assert isinstance(response_data, dict)
            cache[cache_key] = response_data

        items = response_data.get("message", {}).get("items", [])
        if not items:
            break

        offset += params["rows"]
        n_results += 1

    return n_results


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
    for journal in issns:
        issn = issns[journal]["print_issn"]
        for date_range in date_ranges:
            date_range["journal"] = journal
            pprint(date_range)
            n_results = fetch_crossref_metadata(
                date_from=date_range["date_from"],
                date_to=date_range["date_to"],
                issn=issn,
                cache=cache,
                user_email=user_email,
            )

    keys = list(cache)
    pprint(keys)
