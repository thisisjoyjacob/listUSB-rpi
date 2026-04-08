from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from listusb.cli import TYPE_ALIASES, _resolve_type, main
from listusb.models import USBDevice


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_devices():
    return [
        USBDevice(
            path="/dev/ttyUSB0",
            name="FT232R",
            serial="FTDI_FT232R_A50285BI",
            vendor="FTDI",
            vid="0403",
            pid="6001",
            subsystem="tty",
        ),
    ]


class TestResolveType:
    def test_serial_alias(self):
        assert _resolve_type("serial") == "tty"

    def test_storage_alias(self):
        assert _resolve_type("storage") == "block"

    def test_camera_alias(self):
        assert _resolve_type("camera") == "video4linux"

    def test_case_insensitive(self):
        assert _resolve_type("Serial") == "tty"

    def test_raw_subsystem_passthrough(self):
        assert _resolve_type("tty") == "tty"

    def test_unknown_passthrough(self):
        assert _resolve_type("custom_subsystem") == "custom_subsystem"

    def test_none(self):
        assert _resolve_type(None) is None


class TestCLI:
    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_default_table_output(self, mock_require, mock_scan, runner, mock_devices):
        mock_scan.return_value = mock_devices
        result = runner.invoke(main)
        assert result.exit_code == 0
        assert "/dev/ttyUSB0" in result.output
        assert "FT232R" in result.output

    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_json_output(self, mock_require, mock_scan, runner, mock_devices):
        mock_scan.return_value = mock_devices
        result = runner.invoke(main, ["--json"])
        assert result.exit_code == 0
        import json

        parsed = json.loads(result.output)
        assert isinstance(parsed, list)
        assert parsed[0]["path"] == "/dev/ttyUSB0"

    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_csv_output(self, mock_require, mock_scan, runner, mock_devices):
        mock_scan.return_value = mock_devices
        result = runner.invoke(main, ["--csv"])
        assert result.exit_code == 0
        assert "path" in result.output
        assert "/dev/ttyUSB0" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "listusb-rpi" in result.output

    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_vendor_filter(self, mock_require, mock_scan, runner, mock_devices):
        mock_scan.return_value = mock_devices
        result = runner.invoke(main, ["--vendor", "FTDI"])
        assert result.exit_code == 0
        assert "/dev/ttyUSB0" in result.output

    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_vendor_filter_no_match(self, mock_require, mock_scan, runner, mock_devices):
        mock_scan.return_value = mock_devices
        result = runner.invoke(main, ["--vendor", "Nonexistent"])
        assert result.exit_code == 0
        assert "No USB devices found." in result.output

    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_type_alias(self, mock_require, mock_scan, runner, mock_devices):
        mock_scan.return_value = mock_devices
        result = runner.invoke(main, ["--type", "serial"])
        assert result.exit_code == 0
        assert "/dev/ttyUSB0" in result.output

    @patch("listusb.scanner.scan")
    @patch("listusb.scanner.require_linux")
    def test_empty_results(self, mock_require, mock_scan, runner):
        mock_scan.return_value = []
        result = runner.invoke(main)
        assert result.exit_code == 0
        assert "No USB devices found." in result.output
