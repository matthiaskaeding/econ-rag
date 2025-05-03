import pytest

from econ_rag.bm25.clean_data import clean_text
from econ_rag.data.utils import get_issns, make_hive_cache_key, parse_hive_cache_key


def test_make_hive_cache_key():
    # Test basic functionality
    result = make_hive_cache_key(
        issn="0033-5533", date_from="2020-01-01", date_to="2020-12-31", offset=0
    )
    assert result == "date_from=2020-01-01/date_to=2020-12-31/issn=0033-5533/offset=0"

    # Test with different order (should still be sorted)
    result = make_hive_cache_key(
        offset=0, date_to="2020-12-31", date_from="2020-01-01", issn="0033-5533"
    )
    assert result == "date_from=2020-01-01/date_to=2020-12-31/issn=0033-5533/offset=0"


def test_parse_hive_cache_key():
    # Test basic functionality
    cache_key = "issn=0033-5533/date_from=2020-01-01/date_to=2020-12-31/offset=0"
    result = parse_hive_cache_key(cache_key)
    assert result == {
        "issn": "0033-5533",
        "date_from": "2020-01-01",
        "date_to": "2020-12-31",
        "offset": "0",
    }

    # Test with single key-value pair
    result = parse_hive_cache_key("issn=0033-5533")
    assert result == {"issn": "0033-5533"}

    # Test with malformed input (should raise AssertionError)
    with pytest.raises(ValueError):
        parse_hive_cache_key("malformed-key")

        result = parse_hive_cache_key("")


def test_get_issns():
    result = get_issns()

    # Test structure
    assert isinstance(result, dict)
    assert len(result) == 5  # Should have 5 journals

    # Test specific journals
    assert "Quarterly Journal of Economics" in result
    assert "American Economic Review" in result
    assert "Journal of Political Economy" in result
    assert "Econometrica" in result
    assert "Review of Economic Studies" in result

    # Test journal structure
    for journal in result.values():
        assert "print_issn" in journal
        assert "online_issn" in journal
        assert isinstance(journal["print_issn"], str)
        assert isinstance(journal["online_issn"], str)

    # Test specific ISSNs
    assert result["Quarterly Journal of Economics"]["print_issn"] == "0033-5533"
    assert result["American Economic Review"]["print_issn"] == "0002-8282"
    assert result["Journal of Political Economy"]["print_issn"] == "0022-3808"
    assert result["Econometrica"]["print_issn"] == "0012-9682"
    assert result["Review of Economic Studies"]["print_issn"] == "0034-6527"


def test_clean_text():
    # Test basic functionality
    assert clean_text("  hello  world  ") == "hello world"
    assert clean_text("hello\nworld") == "hello world"
    assert clean_text("hello\tworld") == "hello world"

    # Test multiple spaces and newlines
    assert clean_text("hello    world\n\n\n") == "hello world"
    assert clean_text("hello\n\n\nworld") == "hello world"

    # Test empty string
    assert clean_text("") == ""

    # Test non-string input

    with pytest.raises(AssertionError):
        assert clean_text(None) == ""
        assert clean_text(123) == ""

    # Test with special characters
    assert clean_text("hello-world") == "hello-world"
