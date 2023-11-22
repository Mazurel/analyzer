from src.itertools import contains_at_least_n, find_left


def test_contains_at_least_n():
    it = range(10)

    assert contains_at_least_n(it, 2, lambda i: i % 2 == 0)
    assert not contains_at_least_n(it, 6, lambda i: i % 2 == 0)


def test_find_left():
    ls = [1, 3, 2, 5, 6, 7, 4, 9]

    assert (i := find_left(ls, lambda e: e % 2 == 0)) == 2
    assert (i := find_left(ls, lambda e: e % 2 == 0, i + 1)) == 4
    assert (i := find_left(ls, lambda e: e % 2 == 0, i + 1)) == 6
    assert (i := find_left(ls, lambda e: e % 2 == 0, i + 1)) == -1

    assert find_left(ls, lambda e: e % 2 == 0, -1) == -1
