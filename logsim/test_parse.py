"""Test the network module."""
import pytest

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

@pytest.fixture
def new_parser():
    """Return a new instance of the Parser class."""
   
    test_file_path = "tests/example2.txt"

    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(test_file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return parser

def test_1(new_parser):

    new_parser.parse_network()
