"""Test the names module"""
import pytest

from names import Names


@pytest.fixture
def names_with_entries():
    new_names = Names()
    new_names.lookup(["Zero", "One", "Two"])
    return new_names


def test_lookup():
    new_names = Names()
    assert [0] == new_names.lookup(["Zero"])  # Adding new name
    assert [0, 1] == new_names.lookup(["Zero", "One"])
    # An existing name and a new name
    IDs = new_names.lookup(["Two", "Three"])  # Two new names
    assert IDs == new_names.lookup(["Two", "Three"])
    assert [3, 0, 2, 1] == new_names.lookup(
        ["Three", "Zero", "Two", "One"])  # All four names random order


def test_query(names_with_entries):
    assert [0, 1, 2] == [names_with_entries.query(item)
                         for item in ["Zero", "One", "Two"]]
    assert (names_with_entries.query("nonexistant") is None)
