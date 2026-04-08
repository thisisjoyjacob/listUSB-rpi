from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from typing import Optional

# slots=True requires Python 3.10+; use it when available for memory efficiency
_DATACLASS_KWARGS = {"frozen": True}
if sys.version_info >= (3, 10):
    _DATACLASS_KWARGS["slots"] = True


def _frozen_dataclass(cls):
    """Apply @dataclass(frozen=True, slots=True) with Python 3.9 compat."""
    return dataclass(**_DATACLASS_KWARGS)(cls)


@_frozen_dataclass
class USBDevice:
    """Represents a single USB device discovered via udev/sysfs."""

    path: str  # e.g. "/dev/ttyUSB0"
    name: str  # ID_MODEL or fallback
    serial: Optional[str] = None  # ID_SERIAL
    vendor: Optional[str] = None  # ID_VENDOR_FROM_DATABASE or ID_VENDOR
    product: Optional[str] = None  # ID_MODEL_FROM_DATABASE or ID_MODEL
    vid: Optional[str] = None  # ID_VENDOR_ID, e.g. "0403"
    pid: Optional[str] = None  # ID_MODEL_ID, e.g. "6001"
    speed: Optional[str] = None  # sysfs speed attribute
    driver: Optional[str] = None  # DRIVER property
    subsystem: Optional[str] = None  # e.g. "tty", "block"
    sys_path: Optional[str] = None  # raw sysfs path

    def to_dict(self) -> dict:
        return asdict(self)


@_frozen_dataclass
class USBEvent:
    """A hotplug event (add/remove)."""

    action: str  # "add" or "remove"
    device: USBDevice
