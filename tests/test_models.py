from __future__ import annotations

import pytest

from listusb.models import USBDevice, USBEvent


class TestUSBDevice:
    def test_construction_all_fields(self):
        dev = USBDevice(
            path="/dev/ttyUSB0",
            name="FT232R",
            serial="ABC123",
            vendor="FTDI",
            product="FT232R USB UART",
            vid="0403",
            pid="6001",
            speed="12",
            driver="ftdi_sio",
            subsystem="tty",
            sys_path="/sys/devices/test",
        )
        assert dev.path == "/dev/ttyUSB0"
        assert dev.name == "FT232R"
        assert dev.serial == "ABC123"
        assert dev.vid == "0403"
        assert dev.pid == "6001"

    def test_construction_minimal(self):
        dev = USBDevice(path="/dev/sda", name="USB Drive")
        assert dev.path == "/dev/sda"
        assert dev.name == "USB Drive"
        assert dev.serial is None
        assert dev.vendor is None
        assert dev.vid is None

    def test_frozen_raises_on_mutation(self):
        dev = USBDevice(path="/dev/ttyUSB0", name="test")
        with pytest.raises(AttributeError):
            dev.path = "/dev/ttyUSB1"

    def test_to_dict(self):
        dev = USBDevice(
            path="/dev/ttyUSB0",
            name="test",
            serial="SER123",
            vid="0403",
            pid="6001",
        )
        d = dev.to_dict()
        assert isinstance(d, dict)
        assert d["path"] == "/dev/ttyUSB0"
        assert d["serial"] == "SER123"
        assert d["vendor"] is None
        assert "path" in d
        assert "name" in d
        assert "sys_path" in d

    def test_to_dict_contains_all_fields(self):
        dev = USBDevice(path="/dev/x", name="x")
        d = dev.to_dict()
        expected_fields = {
            "path", "name", "serial", "vendor", "product",
            "vid", "pid", "speed", "driver", "subsystem", "sys_path",
        }
        assert set(d.keys()) == expected_fields


class TestUSBEvent:
    def test_construction(self):
        dev = USBDevice(path="/dev/ttyUSB0", name="test")
        event = USBEvent(action="add", device=dev)
        assert event.action == "add"
        assert event.device.path == "/dev/ttyUSB0"

    def test_remove_event(self):
        dev = USBDevice(path="/dev/sda", name="drive")
        event = USBEvent(action="remove", device=dev)
        assert event.action == "remove"
