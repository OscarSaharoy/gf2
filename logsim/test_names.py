"""Test the names module"""
import pytest

from names import Names


def test_lookup():
    new_names = Names()
    assert [0] == new_names.lookup(["Zero"])  # Adding new name
    # An existing name and a new name
    assert [0, 1] == new_names.lookup(["Zero", "One"])
    [ID2, ID3] = new_names.lookup(["Two", "Three"])  # Two new names
    # Check that the IDs for the names are correct
    assert [ID2, ID3] == new_names.lookup(["Two", "Three"])
    assert [ID3, 0, ID2, 1] == new_names.lookup(
        ["Three", "Zero", "Two", "One"])  # All four names random order


def test_query():
    new_names = Names()
    IDs = new_names.lookup(["Zero", "One", "Two"])  # Populate names
    # Test query for a set of present names
    assert IDs == [names_with_entries.query(item)
                         for item in ["Zero", "One", "Two"]]
    # Check that querying an absent name returns None
    assert (names_with_entries.query("nonexistant") is None)
    
