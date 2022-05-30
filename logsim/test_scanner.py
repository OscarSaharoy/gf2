"""Test the scanner module"""
# import pytest
from scanner import Scanner, Symbol
from names import Names


def test_example_symbols():

    new_names = Names()
    new_scanner = Scanner("logsim/tests/example1.txt", new_names)

    EOF = Symbol(sym_type=new_scanner.EOF)

    symbols = [new_scanner.get_symbol()]

    while not symbols[-1] == EOF:
        new_symbol = new_scanner.get_symbol()
        symbols.append(new_symbol)
    assert symbols[0].type == new_scanner.KEYWORD
    assert symbols[1].type == new_scanner.B_OPEN
    assert symbols[2].type == new_scanner.B_CLOSE
    assert symbols[3].type == new_scanner.SEMICOLON
    assert symbols[4].type == new_scanner.KEYWORD
    assert symbols[5].type == new_scanner.EOF
