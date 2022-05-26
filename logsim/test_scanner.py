"""Test the scanner module"""
import pytest
from scanner import Scanner, Symbol
from names import Names

def test_example_symbols():
    new_names = Names()
    new_scanner = Scanner("tests/example1.txt", new_names)

    EOF = Symbol(Scanner.EOF)
    
    symbols = [Scanner.get_symbol()]
    
    while not symbols[-1] == EOF:
        new_symbol = Scanner.get_symbol()
        symbols.append(new_symbol)
