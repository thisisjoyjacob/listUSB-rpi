from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestWatch:
    @patch("listusb.monitor._HAS_PYUDEV", True)
    @patch("listusb.monitor.require_linux")
    @patch("listusb.monitor.pyudev", create=True)
    def test_yields_add_event(self, mock_pyudev, mock_require):
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(
            properties={
                "DEVNAME": "/dev/ttyUSB0",
                "ID_SERIAL": "test_serial",
                "ID_MODEL": "TestDevice",
            },
        )
        device.action = "add"

        mock_monitor = MagicMock()
        mock_pyudev.Context.return_value = MagicMock()
        mock_pyudev.Monitor.from_netlink.return_value = mock_monitor

        # poll returns one device then None (stops iteration)
        mock_monitor.poll = MagicMock(side_effect=[device, None])

        from listusb.monitor import watch

        events = list(watch())
        assert len(events) == 1
        assert events[0].action == "add"
        assert events[0].device.path == "/dev/ttyUSB0"

    @patch("listusb.monitor._HAS_PYUDEV", True)
    @patch("listusb.monitor.require_linux")
    @patch("listusb.monitor.pyudev", create=True)
    def test_yields_remove_event(self, mock_pyudev, mock_require):
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(
            properties={
                "DEVNAME": "/dev/ttyUSB0",
                "ID_SERIAL": "test_serial",
                "ID_MODEL": "TestDevice",
            },
        )
        device.action = "remove"

        mock_monitor = MagicMock()
        mock_pyudev.Context.return_value = MagicMock()
        mock_pyudev.Monitor.from_netlink.return_value = mock_monitor
        mock_monitor.poll = MagicMock(side_effect=[device, None])

        from listusb.monitor import watch

        events = list(watch())
        assert len(events) == 1
        assert events[0].action == "remove"

    @patch("listusb.monitor._HAS_PYUDEV", True)
    @patch("listusb.monitor.require_linux")
    @patch("listusb.monitor.pyudev", create=True)
    def test_skips_non_add_remove_actions(self, mock_pyudev, mock_require):
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(
            properties={
                "DEVNAME": "/dev/ttyUSB0",
                "ID_SERIAL": "test_serial",
                "ID_MODEL": "TestDevice",
            },
        )
        device.action = "change"

        mock_monitor = MagicMock()
        mock_pyudev.Context.return_value = MagicMock()
        mock_pyudev.Monitor.from_netlink.return_value = mock_monitor
        mock_monitor.poll = MagicMock(side_effect=[device, None])

        from listusb.monitor import watch

        events = list(watch())
        assert len(events) == 0

    @patch("listusb.monitor._HAS_PYUDEV", True)
    @patch("listusb.monitor.require_linux")
    @patch("listusb.monitor.pyudev", create=True)
    def test_skips_devices_without_serial(self, mock_pyudev, mock_require):
        from tests.conftest import make_mock_udev_device

        device = make_mock_udev_device(
            properties={"DEVNAME": "/dev/ttyS0"},
        )
        device.action = "add"

        mock_monitor = MagicMock()
        mock_pyudev.Context.return_value = MagicMock()
        mock_pyudev.Monitor.from_netlink.return_value = mock_monitor
        mock_monitor.poll = MagicMock(side_effect=[device, None])

        from listusb.monitor import watch

        events = list(watch())
        assert len(events) == 0

    @patch("listusb.monitor._HAS_PYUDEV", False)
    @patch("listusb.monitor.require_linux")
    def test_raises_without_pyudev(self, mock_require):
        from listusb.monitor import watch

        with pytest.raises(RuntimeError, match="pyudev"):
            list(watch())
