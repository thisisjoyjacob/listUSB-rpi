from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path
from typing import Optional

from listusb._platform import require_linux
from listusb.models import USBDevice

logger = logging.getLogger(__name__)

# Try importing pyudev; fall back to sysfs-only scanning if unavailable
try:
    import pyudev

    _HAS_PYUDEV = True
except ImportError:
    _HAS_PYUDEV = False


def _has_usb_ancestor(device: pyudev.Device) -> bool:
    """Check if a pyudev device has a USB ancestor in its parent chain."""
    parent = device.parent
    while parent is not None:
        if parent.subsystem == "usb":
            return True
        parent = parent.parent
    return False


def _get_speed(device: pyudev.Device) -> Optional[str]:
    """Get USB speed by walking the parent chain to find a USB device with speed attr."""
    current = device
    while current is not None:
        try:
            speed = current.attributes.get("speed")
            if speed:
                return speed.decode("utf-8", errors="replace").strip()
        except (KeyError, AttributeError):
            pass
        current = current.parent
    return None


def _device_from_udev(dev: pyudev.Device) -> Optional[USBDevice]:
    """Convert a pyudev.Device to USBDevice, or None if it should be skipped.

    Skip logic mirrors the original bash script:
    - Skip devices whose devname starts with "bus/" (USB host controllers)
    - Skip devices with no ID_SERIAL
    """
    devname = dev.get("DEVNAME")
    if not devname:
        return None
    if devname.startswith("/dev/bus/"):
        return None
    serial = dev.get("ID_SERIAL")
    if not serial:
        return None

    return USBDevice(
        path=devname,
        name=dev.get("ID_MODEL", dev.get("ID_SERIAL_SHORT", "")),
        serial=serial,
        vendor=dev.get("ID_VENDOR_FROM_DATABASE", dev.get("ID_VENDOR")),
        product=dev.get("ID_MODEL_FROM_DATABASE", dev.get("ID_MODEL")),
        vid=dev.get("ID_VENDOR_ID"),
        pid=dev.get("ID_MODEL_ID"),
        speed=_get_speed(dev),
        driver=dev.get("DRIVER"),
        subsystem=dev.subsystem,
        sys_path=dev.sys_path,
    )


def _scan_pyudev() -> list[USBDevice]:
    """Scan using pyudev — enumerate all subsystems, filter by USB parentage."""
    ctx = pyudev.Context()
    devices: list[USBDevice] = []
    seen_paths: set[str] = set()

    for dev in ctx.list_devices():
        if not _has_usb_ancestor(dev):
            continue
        try:
            usb_dev = _device_from_udev(dev)
        except PermissionError:
            logger.warning("Permission denied reading device: %s", dev.sys_path)
            continue
        if usb_dev and usb_dev.path not in seen_paths:
            seen_paths.add(usb_dev.path)
            devices.append(usb_dev)

    return devices


def _scan_sysfs() -> list[USBDevice]:
    """Fallback scanner that reads /sys/bus/usb/devices/ directly.

    This mirrors the original bash script approach. Provides fewer properties
    than the pyudev scanner (no vendor database lookups, no driver info).
    """
    devices: list[USBDevice] = []
    seen_paths: set[str] = set()
    usb_devices_path = Path("/sys/bus/usb/devices")

    if not usb_devices_path.exists():
        return devices

    for device_dir in usb_devices_path.iterdir():
        if not device_dir.is_dir():
            continue

        # Look for sub-devices that have a 'dev' file (character/block devices)
        for dev_file in device_dir.rglob("dev"):
            sys_path = dev_file.parent

            # Read uevent to get device properties
            uevent_path = sys_path / "uevent"
            if not uevent_path.exists():
                continue

            try:
                props = {}
                for line in uevent_path.read_text().strip().splitlines():
                    if "=" in line:
                        key, _, value = line.partition("=")
                        props[key] = value

                devname = props.get("DEVNAME")
                if not devname:
                    continue
                devname = f"/dev/{devname}"
                if devname.startswith("/dev/bus/"):
                    continue

                # Try to read serial from various locations
                serial = None
                for attr_name in ("serial", "ID_SERIAL"):
                    attr_path = sys_path / attr_name
                    if attr_path.exists():
                        try:
                            serial = attr_path.read_text().strip()
                            if serial:
                                break
                        except (PermissionError, OSError):
                            continue

                # Walk up to USB parent for serial if not found
                if not serial:
                    parent = sys_path.parent
                    while parent != usb_devices_path and parent != parent.parent:
                        serial_path = parent / "serial"
                        if serial_path.exists():
                            try:
                                serial = serial_path.read_text().strip()
                                if serial:
                                    break
                            except (PermissionError, OSError):
                                pass
                        parent = parent.parent

                if not serial:
                    continue

                if devname in seen_paths:
                    continue
                seen_paths.add(devname)

                # Read optional attributes
                speed = None
                for p in (sys_path, sys_path.parent):
                    speed_path = p / "speed"
                    if speed_path.exists():
                        try:
                            speed = speed_path.read_text().strip()
                            if speed:
                                break
                        except (PermissionError, OSError):
                            pass

                vid = None
                pid = None
                for p in (sys_path, sys_path.parent):
                    vid_path = p / "idVendor"
                    pid_path = p / "idProduct"
                    if vid_path.exists():
                        try:
                            vid = vid_path.read_text().strip()
                        except (PermissionError, OSError):
                            pass
                    if pid_path.exists():
                        try:
                            pid = pid_path.read_text().strip()
                        except (PermissionError, OSError):
                            pass
                    if vid and pid:
                        break

                product = None
                product_path = sys_path / "product"
                if not product_path.exists():
                    product_path = sys_path.parent / "product"
                if product_path.exists():
                    try:
                        product = product_path.read_text().strip()
                    except (PermissionError, OSError):
                        pass

                subsystem = props.get("SUBSYSTEM")

                devices.append(
                    USBDevice(
                        path=devname,
                        name=product or props.get("DEVNAME", ""),
                        serial=serial,
                        vendor=None,  # no vendor database in sysfs fallback
                        product=product,
                        vid=vid,
                        pid=pid,
                        speed=speed,
                        driver=props.get("DRIVER"),
                        subsystem=subsystem,
                        sys_path=str(sys_path),
                    )
                )
            except PermissionError:
                logger.warning("Permission denied reading device: %s", sys_path)
            except OSError as e:
                logger.debug("Error reading device %s: %s", sys_path, e)

    return devices


def scan() -> list[USBDevice]:
    """Return all currently connected USB devices.

    Uses pyudev if available (recommended — install with `pip install listusb-rpi[udev]`).
    Falls back to direct sysfs reading if pyudev is not installed.
    """
    require_linux()

    if _HAS_PYUDEV:
        return _scan_pyudev()
    else:
        warnings.warn(
            "pyudev not installed — using sysfs fallback (fewer device properties). "
            "Install with: pip install listusb-rpi[udev]",
            stacklevel=2,
        )
        return _scan_sysfs()
