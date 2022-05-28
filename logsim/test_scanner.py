"""Test the scanner module"""
import pytest
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
