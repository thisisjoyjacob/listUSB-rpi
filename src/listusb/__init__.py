"""listusb-rpi: List and monitor USB devices on Raspberry Pi and Linux."""
from __future__ import annotations

from listusb._version import __version__
from listusb.models import USBDevice, USBEvent

__all__ = [
    "__version__",
    "USBDevice",
    "USBEvent",
    "devices",
    "find_device",
    "scan",
    "watch",
    "filter_devices",
]


def devices(**filters) -> list[USBDevice]:
    """Scan for USB devices, optionally filtering results.

    Usage:
        from listusb import devices
        all_devices = devices()
        serial_devices = devices(subsystem="tty")
        specific = devices(vid="1a86", pid="7523")
    """
    from listusb.scanner import scan as _scan
    from listusb.filters import filter_devices as _filter

    raw = _scan()
    if filters:
        return _filter(raw, **filters)
    return raw


def find_device(**filters) -> USBDevice | None:
    """Return the first device matching filters, or None."""
    results = devices(**filters)
    return results[0] if results else None


def scan() -> list[USBDevice]:
    """Return all currently connected USB devices (unfiltered)."""
    from listusb.scanner import scan as _scan

    return _scan()


def watch():
    """Yield USBEvent objects for hotplug add/remove events. Blocks indefinitely.

    Requires pyudev. Install with: pip install listusb-rpi[udev]
    """
    from listusb.monitor import watch as _watch

    return _watch()


def filter_devices(devices_list, **filters) -> list[USBDevice]:
    """Filter a list of USBDevices by attributes."""
    from listusb.filters import filter_devices as _filter

    return _filter(devices_list, **filters)
