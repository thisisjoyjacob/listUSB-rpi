from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from listusb.models import USBDevice


def make_mock_udev_device(
    properties: dict,
    attributes: dict | None = None,
    subsystem: str = "tty",
    sys_path: str = "/sys/devices/test",
    parent_subsystem: str = "usb",
):
    """Create a mock pyudev.Device for testing."""
    device = MagicMock()
    device.get = lambda key, default=None: properties.get(key, default)
    device.__getitem__ = lambda self, key: properties[key]
    device.subsystem = subsystem
    device.sys_path = sys_path

    attrs = MagicMock()
    attrs.get = lambda key, default=b"": (attributes or {}).get(key, default)
    device.attributes = attrs

    # Create a USB parent so _has_usb_ancestor returns True
    parent = MagicMock()
    parent.subsystem = parent_subsystem
    parent.parent = None
    parent.attributes = MagicMock()
    parent.attributes.get = lambda key, default=b"": b""
    device.parent = parent

    return device


@pytest.fixture
def ftdi_device():
    """Mock FTDI USB-serial adapter."""
    return make_mock_udev_device(
        properties={
            "DEVNAME": "/dev/ttyUSB0",
            "ID_SERIAL": "FTDI_FT232R_USB_UART_A50285BI",
            "ID_MODEL": "FT232R_USB_UART",
            "ID_VENDOR": "FTDI",
            "ID_VENDOR_FROM_DATABASE": "Future Technology Devices International",
            "ID_MODEL_FROM_DATABASE": "FT232 Serial (UART) IC",
            "ID_VENDOR_ID": "0403",
            "ID_MODEL_ID": "6001",
            "ID_SERIAL_SHORT": "A50285BI",
            "DRIVER": "ftdi_sio",
        },
        attributes={"speed": b"12"},
        subsystem="tty",
    )


@pytest.fixture
def kingston_device():
    """Mock Kingston USB storage device."""
    return make_mock_udev_device(
        properties={
            "DEVNAME": "/dev/sda",
            "ID_SERIAL": "Kingston_DataTraveler_2.0",
            "ID_MODEL": "DataTraveler_2.0",
            "ID_VENDOR": "Kingston",
            "ID_VENDOR_ID": "0951",
            "ID_MODEL_ID": "1666",
        },
        attributes={"speed": b"480"},
        subsystem="block",
    )


@pytest.fixture
def bus_device():
    """Mock USB bus device (should be skipped)."""
    return make_mock_udev_device(
        properties={
            "DEVNAME": "/dev/bus/usb/001/001",
            "ID_SERIAL": "Linux_xhci-hcd_Host_Controller",
        },
        subsystem="usb",
    )


@pytest.fixture
def no_serial_device():
    """Mock device with no serial (should be skipped)."""
    return make_mock_udev_device(
        properties={
            "DEVNAME": "/dev/ttyS0",
        },
        subsystem="tty",
    )


@pytest.fixture
def sample_usb_devices():
    """Pre-built USBDevice instances for testing formatters/filters."""
    return [
        USBDevice(
            path="/dev/ttyUSB0",
            name="FT232R_USB_UART",
            serial="FTDI_FT232R_USB_UART_A50285BI",
            vendor="Future Technology Devices International",
            product="FT232 Serial (UART) IC",
            vid="0403",
            pid="6001",
            speed="12",
            driver="ftdi_sio",
            subsystem="tty",
        ),
        USBDevice(
            path="/dev/sda",
            name="DataTraveler_2.0",
            serial="Kingston_DataTraveler_2.0",
            vendor="Kingston",
            product="DataTraveler 2.0",
            vid="0951",
            pid="1666",
            speed="480",
            driver=None,
            subsystem="block",
        ),
    ]
