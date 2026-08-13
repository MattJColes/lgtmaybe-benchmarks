import pytest


def test_invalid_input_raises():
    with pytest.raises(ValueError, match="invalid date"):
        parse_date("bad")
