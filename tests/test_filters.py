from __future__ import annotations

from listusb.filters import filter_devices
from listusb.models import USBDevice


class TestFilterDevices:
    def test_filter_by_vendor(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, vendor="Future")
        assert len(result) == 1
        assert result[0].path == "/dev/ttyUSB0"

    def test_filter_by_vendor_case_insensitive(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, vendor="future")
        assert len(result) == 1

    def test_filter_by_vendor_substring(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, vendor="Future")
        assert len(result) == 1

    def test_filter_by_vid(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, vid="0951")
        assert len(result) == 1
        assert result[0].path == "/dev/sda"

    def test_filter_by_subsystem(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, subsystem="tty")
        assert len(result) == 1
        assert result[0].path == "/dev/ttyUSB0"

    def test_filter_by_driver(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, driver="ftdi")
        assert len(result) == 1

    def test_multiple_filters(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, vendor="Future", subsystem="tty")
        assert len(result) == 1

    def test_no_matches(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, vendor="Nonexistent")
        assert result == []

    def test_none_field_does_not_crash(self):
        dev = USBDevice(path="/dev/x", name="x", vendor=None)
        result = filter_devices([dev], vendor="test")
        assert result == []

    def test_empty_device_list(self):
        result = filter_devices([], vendor="test")
        assert result == []

    def test_filter_by_name(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, name="FT232R")
        assert len(result) == 1

    def test_filter_by_product(self, sample_usb_devices):
        result = filter_devices(sample_usb_devices, product="DataTraveler")
        assert len(result) == 1
