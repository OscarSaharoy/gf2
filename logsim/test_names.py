"""Test the names module"""
import pytest

from names import Names


def test_lookup():
    new_names = Names()
    assert [0] == new_names.lookup(["Zero"])  # Adding new name
    # An existing name and a new name
    assert [0, 1] == new_names.lookup(["Zero", "One"])
    # Try adding several names at the same time
    assert [2, 3, 4] == new_names.lookup(["Two", "Three",
                                          "Four"])
    # Lookup existing names
    assert [2, 1] == new_names.lookup(["Two", "One"])

    # Test that non-strings raise an error
    with pytest.raises(Exception):
        new_names.lookup(["Hi", 1])


def test_query():
    new_names = Names()
    IDs = new_names.lookup(["Zero", "One", "Two"])  # Populate names
    # Test query for a set of present names
    assert IDs == [new_names.query(item)
                   for item in ["Zero", "One", "Two"]]
    # Check that querying an absent name returns None
    assert (new_names.query("nonexistant") is None)


def test_get_name_string():
    new_names = Names()
    # Populate names
    IDs = new_names.lookup(["Zero", "One", "Two"])
    # Check that the correct names are returned
    assert ["Zero", "One", "Two"] == [new_names.get_name_string(ID)
                                      for ID in IDs]
    # Check that an unused ID number returns None
    assert (new_names.get_name_string(3) is None)
