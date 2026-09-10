import pytest
from src.sizes import parse_size

@pytest.mark.parametrize("text,expected", [
    ("512B", 512), ("1KB", 1024), ("1.5KB", 1536), ("2MB", 2 * 1024**2),
    ("3 GB", 3 * 1024**3), ("1tb", 1024**4), ("  10 mb ", 10 * 1024**2), ("0B", 0),
])
def test_parse_size(text, expected):
    assert parse_size(text) == expected

@pytest.mark.parametrize("text", ["", "abc", "12", "1.5.5KB", "5PB", "-1KB"])
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_size(text)
