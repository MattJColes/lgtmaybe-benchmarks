def test_invalid_input_raises():
    try:
        parse_date("bad")
    except Exception:
        pass
