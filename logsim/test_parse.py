"""Test the network module."""
import pytest

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


@pytest.fixture
def new_parser(path):
    """Return some classes needed to setup the parser."""

    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    new_parser = Parser(names, devices, network, monitors, scanner, True)

    return new_parser


@pytest.mark.parametrize('path', ["logsim/tests/basic.txt"])
def test_basic_parse(new_parser):

    parse_success = new_parser.parse_network()
    assert parse_success


@pytest.mark.parametrize('path', ["logsim/tests/empty.txt"])
def test_empty_file(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 1


@pytest.mark.parametrize('path', ["logsim/tests/nostart.txt"])
def test_no_start(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 1


@pytest.mark.parametrize('path', ["logsim/tests/noend.txt"])
def test_no_end(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 1


@pytest.mark.parametrize('path', ["logsim/tests/baddevices.txt"])
def test_bad_devices(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 2


@pytest.mark.parametrize('path', ["logsim/tests/badtypes.txt"])
def test_bad_types(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/badconnections.txt"])
def test_bad_connections(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 2


@pytest.mark.parametrize('path', ["logsim/tests/badoutputs.txt"])
def test_bad_outputs(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/duplicatestatements.txt"])
def test_duplicate_statements(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/badinputs.txt"])
def test_duplicate_statements(new_parser):

    new_parser.parse_network()
    assert new_parser.error_count == 3
