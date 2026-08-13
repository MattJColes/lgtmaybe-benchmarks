def test_page_empty():
    assert page([], 10) == []


def test_page_exact_boundary():
    assert page(list(range(10)), 10) == [list(range(10))]
