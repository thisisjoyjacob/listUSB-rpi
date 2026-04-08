from __future__ import annotations

import json

from listusb.formatters import format_csv, format_json, format_table
from listusb.models import USBDevice


class TestFormatTable:
    def test_normal_output(self, sample_usb_devices):
        result = format_table(sample_usb_devices)
        assert "PATH" in result
        assert "/dev/ttyUSB0" in result
        assert "/dev/sda" in result
        assert "0403:6001" in result
        assert "0951:1666" in result

    def test_empty_list(self):
        result = format_table([])
        assert result == "No USB devices found."

    def test_missing_fields(self):
        dev = USBDevice(path="/dev/ttyUSB0", name="test")
        result = format_table([dev])
        assert "/dev/ttyUSB0" in result
        assert "----:----" in result


class TestFormatJson:
    def test_valid_json(self, sample_usb_devices):
        result = format_json(sample_usb_devices)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["path"] == "/dev/ttyUSB0"
        assert parsed[1]["vid"] == "0951"

    def test_empty_list(self):
        result = format_json([])
        parsed = json.loads(result)
        assert parsed == []

    def test_none_fields_serialized(self):
        dev = USBDevice(path="/dev/x", name="x")
        result = format_json([dev])
        parsed = json.loads(result)
        assert parsed[0]["vendor"] is None


class TestFormatCsv:
    def test_header_and_rows(self, sample_usb_devices):
        result = format_csv(sample_usb_devices)
        lines = result.strip().splitlines()
        assert len(lines) == 3  # header + 2 data rows
        assert "path" in lines[0]
        assert "/dev/ttyUSB0" in lines[1]

    def test_empty_list(self):
        result = format_csv([])
        assert result == ""
