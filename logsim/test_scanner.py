"""Test the scanner module"""
# import pytest
from scanner import Scanner, Symbol
from names import Names


@pytest.fixture
def new_scanner():
    new_names = Names()
    return Scanner("logsim/tests/example1.txt", new_names)


@pytest.fixture
def symbols(new_scanner):
    EOF = Symbol(sym_type=new_scanner.EOF)
    symbol_list = [new_scanner.get_symbol()]

    while not symbol_list[-1] == EOF:
        new_symbol = new_scanner.get_symbol()
        symbol_list.append(new_symbol)
    return symbol_list


def test_symbol_types(symbols, new_scanner):
    assert symbols[0].type == new_scanner.KEYWORD
    assert symbols[1].type == new_scanner.B_OPEN
    assert symbols[2].type == new_scanner.B_CLOSE
    assert symbols[3].type == new_scanner.SEMICOLON
    assert symbols[4].type == new_scanner.KEYWORD
    assert symbols[5].type == new_scanner.EOF


def test_symbol_ids(symbols, new_scanner):
    assert symbols[0].id == new_scanner.names.query("START")
    assert symbols[4].id == new_scanner.names.query("END")
