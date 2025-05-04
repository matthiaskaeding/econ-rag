import pytest
from data_prep.process_data import clean_text
from data_prep.utils import get_issns, make_hive_cache_key, parse_hive_cache_key


def test_make_hive_cache_key():
    # Test basic functionality
    got = make_hive_cache_key(
        issn="0033-5533", date_from="2020-01-01", date_to="2020-12-31", offset=0
    )
    want = "date_from=2020-01-01|date_to=2020-12-31|issn=0033-5533|offset=0"
    assert got == want

    # Test with different order (should still be sorted)
    got = make_hive_cache_key(
        offset=0, date_to="2020-12-31", date_from="2020-01-01", issn="0033-5533"
    )
    assert got == want


def test_parse_hive_cache_key():
    # Test basic functionality
    cache_key = "issn=0033-5533|date_from=2020-01-01|date_to=2020-12-31|offset=0"
    result = parse_hive_cache_key(cache_key)
    assert result == {
        "issn": "0033-5533",
        "date_from": "2020-01-01",
        "date_to": "2020-12-31",
        "offset": "0",
    }

    # Test with minimal key
    result = parse_hive_cache_key("issn=0033-5533")
    assert result == {"issn": "0033-5533"}

    # Test with malformed key
    with pytest.raises(ValueError):
        parse_hive_cache_key("malformed-key")

    # Test with empty key
    result = parse_hive_cache_key("")
    assert result == {}


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
        assert "print" in journal
        assert "online" in journal
        assert isinstance(journal["print"], str)
        assert isinstance(journal["online"], str)

    # Test specific ISSNs
    assert result["Quarterly Journal of Economics"]["print"] == "0033-5533"
    assert result["American Economic Review"]["print"] == "0002-8282"
    assert result["Journal of Political Economy"]["print"] == "0022-3808"
    assert result["Econometrica"]["print"] == "0012-9682"
    assert result["Review of Economic Studies"]["print"] == "0034-6527"


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
