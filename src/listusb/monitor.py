from __future__ import annotations

from typing import Iterator

from listusb._platform import require_linux
from listusb.models import USBEvent

try:
    import pyudev

    _HAS_PYUDEV = True
except ImportError:
    _HAS_PYUDEV = False


def watch() -> Iterator[USBEvent]:
    """Yield USBEvent objects for hotplug add/remove events. Blocks indefinitely.

    Requires pyudev. Install with: pip install listusb-rpi[udev]

    This is a generator — iterate with a for-loop or call next().
    Intended for use in a dedicated thread or as a main loop.
    """
    require_linux()

    if not _HAS_PYUDEV:
        raise RuntimeError(
            "watch() requires pyudev. Install with: pip install listusb-rpi[udev]"
        )

    from listusb.scanner import _device_from_udev

    ctx = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(ctx)
    monitor.filter_by(subsystem="usb")
    monitor.start()

    for device in iter(monitor.poll, None):
        if device.action not in ("add", "remove"):
            continue
        usb_dev = _device_from_udev(device)
        if usb_dev is None:
            continue
        yield USBEvent(action=device.action, device=usb_dev)
