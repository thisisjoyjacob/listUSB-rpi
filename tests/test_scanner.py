from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from listusb.models import USBDevice


class TestDeviceFromUdev:
    """Test the _device_from_udev conversion function."""

    def test_happy_path(self, ftdi_device):
        from listusb.scanner import _device_from_udev

        result = _device_from_udev(ftdi_device)
        assert result is not None
        assert result.path == "/dev/ttyUSB0"
        assert result.serial == "FTDI_FT232R_USB_UART_A50285BI"
        assert result.name == "FT232R_USB_UART"
        assert result.vendor == "Future Technology Devices International"
        assert result.vid == "0403"
        assert result.pid == "6001"
        assert result.driver == "ftdi_sio"
        assert result.subsystem == "tty"

    def test_skip_bus_device(self, bus_device):
        from listusb.scanner import _device_from_udev

        result = _device_from_udev(bus_device)
        assert result is None

    def test_skip_no_serial(self, no_serial_device):
        from listusb.scanner import _device_from_udev

        result = _device_from_udev(no_serial_device)
        assert result is None

    def test_skip_no_devname(self):
        from listusb.scanner import _device_from_udev
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(properties={})
        result = _device_from_udev(device)
        assert result is None

    def test_partial_properties(self):
        from listusb.scanner import _device_from_udev
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(
            properties={
                "DEVNAME": "/dev/ttyACM0",
                "ID_SERIAL": "some_serial",
                "ID_SERIAL_SHORT": "SHORT",
            },
        )
        result = _device_from_udev(device)
        assert result is not None
        assert result.path == "/dev/ttyACM0"
        assert result.serial == "some_serial"
        assert result.name == "SHORT"  # fallback to ID_SERIAL_SHORT
        assert result.vendor is None
        assert result.vid is None


class TestHasUsbAncestor:
    def test_device_with_usb_parent(self, ftdi_device):
        from listusb.scanner import _has_usb_ancestor

        assert _has_usb_ancestor(ftdi_device) is True

    def test_device_without_usb_parent(self):
        from listusb.scanner import _has_usb_ancestor
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(
            properties={"DEVNAME": "/dev/ttyS0"},
            parent_subsystem="platform",
        )
        assert _has_usb_ancestor(device) is False


class TestScanPyudev:
    @patch("listusb.scanner._HAS_PYUDEV", True)
    @patch("listusb.scanner.pyudev", create=True)
    @patch("listusb.scanner.require_linux")
    def test_scan_returns_devices(self, mock_require, mock_pyudev, ftdi_device, kingston_device):
        from listusb.scanner import scan

        mock_ctx = MagicMock()
        mock_ctx.list_devices.return_value = [ftdi_device, kingston_device]
        mock_pyudev.Context.return_value = mock_ctx

        result = scan()
        assert len(result) == 2
        assert result[0].path == "/dev/ttyUSB0"
        assert result[1].path == "/dev/sda"

    @patch("listusb.scanner._HAS_PYUDEV", True)
    @patch("listusb.scanner.pyudev", create=True)
    @patch("listusb.scanner.require_linux")
    def test_scan_deduplicates(self, mock_require, mock_pyudev, ftdi_device):
        from listusb.scanner import scan

        mock_ctx = MagicMock()
        # Same device appears twice
        mock_ctx.list_devices.return_value = [ftdi_device, ftdi_device]
        mock_pyudev.Context.return_value = mock_ctx

        result = scan()
        assert len(result) == 1

    @patch("listusb.scanner._HAS_PYUDEV", True)
    @patch("listusb.scanner.pyudev", create=True)
    @patch("listusb.scanner.require_linux")
    def test_scan_skips_bus_devices(self, mock_require, mock_pyudev, bus_device, ftdi_device):
        from listusb.scanner import scan

        mock_ctx = MagicMock()
        mock_ctx.list_devices.return_value = [bus_device, ftdi_device]
        mock_pyudev.Context.return_value = mock_ctx

        result = scan()
        assert len(result) == 1
        assert result[0].path == "/dev/ttyUSB0"

    @patch("listusb.scanner._HAS_PYUDEV", True)
    @patch("listusb.scanner.pyudev", create=True)
    @patch("listusb.scanner.require_linux")
    def test_scan_handles_permission_error(self, mock_require, mock_pyudev, ftdi_device):
        from listusb.scanner import scan

        bad_device = MagicMock()
        bad_device.parent = ftdi_device.parent  # has USB ancestor
        bad_device.subsystem = "tty"
        bad_device.sys_path = "/sys/bad"

        def raise_permission(*args, **kwargs):
            raise PermissionError("Access denied")

        bad_device.get = raise_permission

        mock_ctx = MagicMock()
        mock_ctx.list_devices.return_value = [bad_device, ftdi_device]
        mock_pyudev.Context.return_value = mock_ctx

        # Should not crash, should skip the bad device
        result = scan()
        assert len(result) == 1


class TestPlatformGate:
    @patch("listusb._platform.sys")
    def test_require_linux_raises_on_non_linux(self, mock_sys):
        from listusb._platform import require_linux

        mock_sys.platform = "win32"
        with pytest.raises(RuntimeError, match="requires Linux"):
            require_linux()

    @patch("listusb._platform.sys")
    def test_require_linux_passes_on_linux(self, mock_sys):
        from listusb._platform import require_linux

        mock_sys.platform = "linux"
        require_linux()  # should not raise
