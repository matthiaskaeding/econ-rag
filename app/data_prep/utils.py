def make_hive_cache_key(**kwargs) -> str:
    """
    Construct a Hive-style cache key from keyword arguments in Hive-style format.
    Example: "issn=0033-5533/date_from=2020-01-01/date_to=2020-12-31/offset=0"
    """
    return "/".join(f"{key}={value}" for key, value in sorted(kwargs.items()))


def parse_hive_cache_key(cache_key: str) -> dict:
    """
    Parse a Hive-style cache key string into a dictionary.
    Example usage:
    >>> parse_hive_cache_key("issn=0033-5533/date_from=2020-01-01/date_to=2020-12-31/offset=0")
    {'issn': '0033-5533', 'date_from': '2020-01-01', 'date_to': '2020-12-31', 'offset': '0'}
    """
    pairs = cache_key.split("/")
    result = {}

    for pair in pairs:
        if "=" not in pair:
            msg = "Must contain ="
            raise ValueError(msg)
        key, value = pair.split("=")
        result[key] = value

    return result


def get_issns() -> dict:
    """Returns dict of issns for top 5"""
    return {
        "Quarterly Journal of Economics": {
            "print": "0033-5533",
            "online": "1531-4650",
        },
        "American Economic Review": {
            "print": "0002-8282",
            "online": "1944-7981",
        },
        "Journal of Political Economy": {
            "print": "0022-3808",
            "online": "1537-534X",
        },
        "Econometrica": {"print": "0012-9682", "online": "1468-0262"},
        "Review of Economic Studies": {
            "print": "0034-6527",
            "online": "1467-937X",
        },
    }


def get_journals_by_issn() -> dict:
    """
    Returns a dictionary mapping ISSNs to journal names.
    Example:
    {
        "0033-5533": "Quarterly Journal of Economics",
        "1531-4650": "Quarterly Journal of Economics",
        "0002-8282": "American Economic Review",
        ...
    }
    """
    issns = get_issns()
    result = {}

    for journal_name, issn_dict in issns.items():
        result[issn_dict["print"]] = journal_name
        result[issn_dict["online"]] = journal_name

    return result
