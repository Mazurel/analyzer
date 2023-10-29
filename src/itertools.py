from typing import Iterable, TypeVar, Callable, List

T = TypeVar("T")

def contains_at_least_n(it: Iterable[T], n: int, predicate: Callable[[T], bool]) -> bool:
    """
    Returns `True` if iterator `it` contains at least `n` elements
    that return `True` when given as an argument to the `predicate`
    method.

    This method evaluates predicate and counting lazily,
    so it should be quire effective and fast.
    """
    assert n > 0, "`n` must be greater than zero"
    acc = 0
    for i in it:
        acc += 1 if predicate(i) else 0
        if acc >= n:
            return True

    return False

def find_left(ls: List[T], predicate: Callable[[T], bool], start_index=0) -> int:
    """
    Find index of the first element in `ls` matching `predicate`.

    Additionaly, it is possible to specify starting index by `start_index`.

    Returns -1 when nothing is found,
               when `start_index > len(ls)`, or
               when `start_index < 0`.
    """
    if start_index < 0:
        return -1

    if start_index >= len(ls):
        return -1


    for i, e in enumerate(ls[start_index:]):
        if predicate(e):
            return i + start_index

    return -1

