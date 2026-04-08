from __future__ import annotations

import csv
import io
import json
from typing import Sequence

from listusb.models import USBDevice


def format_table(devices: Sequence[USBDevice]) -> str:
    """Human-readable table. Default CLI output."""
    if not devices:
        return "No USB devices found."

    lines = []
    header = f"{'PATH':<20} {'NAME':<30} {'SERIAL':<30} {'VID:PID':<12}"
    lines.append(header)
    lines.append("-" * len(header))
    for d in devices:
        vidpid = f"{d.vid or '----'}:{d.pid or '----'}"
        lines.append(
            f"{d.path:<20} {(d.name or ''):<30} {(d.serial or ''):<30} {vidpid:<12}"
        )
    return "\n".join(lines)


def format_json(devices: Sequence[USBDevice]) -> str:
    """JSON array output."""
    return json.dumps([d.to_dict() for d in devices], indent=2)


def format_csv(devices: Sequence[USBDevice]) -> str:
    """CSV output with header row."""
    if not devices:
        return ""

    buf = io.StringIO()
    fields = list(devices[0].to_dict().keys())
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for d in devices:
        writer.writerow(d.to_dict())
    return buf.getvalue()
