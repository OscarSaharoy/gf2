"""Test the names module"""
import pytest

from names import Names


@pytest.fixture
def names_with_entries():
    new_names = Names()
    new_names.lookup(["Zero", "One", "Two"])
    return new_names


def test_lookup(names_with_entries):
    new_names = Names()
    assert [0] == new_names.lookup(["Zero"])
    assert [1, 2] == new_names.lookup(["One", "Two"])
    assert [3] == new_names.lookup(["Three"])
    assert [1, 2] == new_names.lookup(["One", "Two"])

def test_query(names_with_entries):
    assert [0, 1, 2] == [names_with_entries.query(item)
                         for item in ["Zero", "One", "Two"]]
    assert (names_with_entries.query(["string"]) is None)
