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
    """Return a new parser initialised with the file at path."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    new_parser = Parser(names, devices, network, monitors, scanner, True)

    return new_parser


@pytest.fixture
def new_classes(path):
    """Return some classes needed to setup the parser."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner, True)

    return devices, network, monitors, parser


@pytest.mark.parametrize('path', ["logsim/tests/basic.txt"])
def test_basic_parse(new_parser):
    """Check that the parser can handle a normal input file."""
    parse_success = new_parser.parse_network()
    assert parse_success


@pytest.mark.parametrize('path', ["logsim/tests/empty.txt"])
def test_empty_file(new_parser):
    """Check that the parser throws one error for an empty input file."""
    new_parser.parse_network()
    assert new_parser.error_count == 1


@pytest.mark.parametrize('path', ["logsim/tests/nostart.txt"])
def test_no_start(new_parser):
    """Check the parser recognises a lack of the START keyword."""
    new_parser.parse_network()
    assert new_parser.error_count == 1


@pytest.mark.parametrize('path', ["logsim/tests/noend.txt"])
def test_no_end(new_parser):
    """Check the parser can recognise lack of the END keyword."""
    new_parser.parse_network()
    assert new_parser.error_count == 1


@pytest.mark.parametrize('path', ["logsim/tests/baddevices.txt"])
def test_bad_devices(new_parser):
    """Check the parser handles syntax errors in the devices block."""
    new_parser.parse_network()
    assert new_parser.error_count == 2


@pytest.mark.parametrize('path', ["logsim/tests/badtypes.txt"])
def test_bad_types(new_parser):
    """Check the parser recognises incorrect device type names."""
    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/badconnections.txt"])
def test_bad_connections(new_parser):
    """Check the parser handles syntax errors in the connections block."""
    new_parser.parse_network()
    assert new_parser.error_count == 2


@pytest.mark.parametrize('path', ["logsim/tests/badoutputs.txt"])
def test_bad_outputs(new_parser):
    """Check the parser handles syntax errors in the outputs block."""
    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/duplicatestatements.txt"])
def test_duplicate_statements(new_parser):
    """Check the parser identifies duplicate statements in the input file."""
    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/badinputs.txt"])
def test_bad_inputs(new_parser):
    """Check the parser recognises semantic errors in the inputs."""
    new_parser.parse_network()
    assert new_parser.error_count == 3


@pytest.mark.parametrize('path', ["logsim/tests/basic.txt"])
def test_devices_integration(new_classes):
    """Check the parser correctly sets up the devices."""
    devices, network, monitors, parser = new_classes

    parser.parse_network()
    assert len(devices.find_devices()) == 3
    assert len(devices.find_devices(devices.CLOCK)) == 2
    assert len(devices.find_devices(devices.OR)) == 1


@pytest.mark.parametrize('path', ["logsim/tests/basic.txt"])
def test_monitors_integration(new_classes):
    """Check the parser correctly sets up monitors."""
    devices, network, monitors, parser = new_classes

    parser.parse_network()
    assert len(monitors.get_signal_names()[0]) == 1
    assert len(monitors.get_signal_names()[1]) == 2


@pytest.mark.parametrize('path', ["logsim/tests/basic.txt"])
def test_network_integration(new_classes):
    """Check the network is built correctly by the parser."""
    devices, network, monitors, parser = new_classes

    parser.parse_network()
    assert network.check_network()
    network.execute_network()


@pytest.mark.parametrize('path', ["logsim/tests/ir2_counter.txt"])
def test_i21_counter(new_classes):
    """Check the parser parses the interrim report 1 counter."""
    devices, network, monitors, parser = new_classes

    assert parser.parse_network()
    assert network.execute_network()


@pytest.mark.parametrize('path', ["logsim/tests/ir2_adder.txt"])
def test_ir1_adder(new_classes):
    """Check the parser parses the interrim report 1 adder."""
    devices, network, monitors, parser = new_classes

    assert parser.parse_network()
    assert network.execute_network()
