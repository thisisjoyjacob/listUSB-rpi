from __future__ import annotations

from typing import Optional, Sequence

from listusb.models import USBDevice


def filter_devices(
    devices: Sequence[USBDevice],
    *,
    vendor: Optional[str] = None,
    product: Optional[str] = None,
    vid: Optional[str] = None,
    pid: Optional[str] = None,
    subsystem: Optional[str] = None,
    driver: Optional[str] = None,
    name: Optional[str] = None,
) -> list[USBDevice]:
    """Filter a list of USBDevices. All filters are case-insensitive substring matches."""
    result = list(devices)
    for attr, value in [
        ("vendor", vendor),
        ("product", product),
        ("vid", vid),
        ("pid", pid),
        ("subsystem", subsystem),
        ("driver", driver),
        ("name", name),
    ]:
        if value is not None:
            value_lower = value.lower()
            result = [
                d
                for d in result
                if getattr(d, attr) and value_lower in getattr(d, attr).lower()
            ]
    return result
