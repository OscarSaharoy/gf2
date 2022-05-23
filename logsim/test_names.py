"""Test the names module"""
import pytest

from names import Names

@pytest.fixture
def names_with_entries():
    new_names = Names()
    IDs = new_names.lookup(["And1", "Nor1", "Sw1"])
    return new_names


def test_lookup(names_with_entries):
    assert [0,1,2] == new_names.lookup(["And1", "Nor1", "Sw1"])
    
    assert [3] == new_names.lookup(["string"])
    

def test_query(names_with_entries):
    assert [0,1,2] == [new_names.query(item) for item in ["And1", "Nor1", "Sw1"]]
    
    assert (new_names.query(["string"]) is None)
