import sys


def require_linux() -> None:
    """Raise RuntimeError if not on Linux. Called by scan()/watch(), not at import time."""
    if sys.platform != "linux":
        raise RuntimeError(
            "listusb-rpi requires Linux (sysfs + udev). "
            f"Current platform: {sys.platform}"
        )
