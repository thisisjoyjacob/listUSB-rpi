from __future__ import annotations

import click

from listusb._version import __version__

# Friendly type aliases mapping user-facing names to Linux subsystem names
TYPE_ALIASES = {
    "serial": "tty",
    "storage": "block",
    "camera": "video4linux",
    "audio": "sound",
    "network": "net",
    "input": "input",
}


def _resolve_type(type_name: str | None) -> str | None:
    """Resolve a friendly type alias to a subsystem name."""
    if type_name is None:
        return None
    return TYPE_ALIASES.get(type_name.lower(), type_name)


@click.command()
@click.version_option(__version__, prog_name="listusb-rpi")
@click.option("--json", "fmt", flag_value="json", help="Output as JSON")
@click.option("--csv", "fmt", flag_value="csv", help="Output as CSV")
@click.option("--table", "fmt", flag_value="table", default=True, help="Output as table (default)")
@click.option("--vendor", default=None, help="Filter by vendor name (substring)")
@click.option("--vid", default=None, help="Filter by vendor ID")
@click.option("--pid", default=None, help="Filter by product ID")
@click.option(
    "--type",
    "device_type",
    default=None,
    help="Filter by type: serial, storage, camera, audio, network (or raw subsystem name)",
)
@click.option("--driver", default=None, help="Filter by driver name")
@click.option("--watch", "watch_mode", is_flag=True, help="Watch for hotplug events")
def main(fmt, vendor, vid, pid, device_type, driver, watch_mode):
    """List USB devices on Raspberry Pi / Linux."""
    subsystem = _resolve_type(device_type)

    if watch_mode:
        _run_watch(fmt, vendor=vendor, vid=vid, pid=pid, subsystem=subsystem, driver=driver)
        return

    from listusb import devices
    from listusb.formatters import format_csv, format_json, format_table

    filters = {
        k: v
        for k, v in dict(
            vendor=vendor, vid=vid, pid=pid, subsystem=subsystem, driver=driver
        ).items()
        if v is not None
    }

    devs = devices(**filters)

    formatter = {"json": format_json, "csv": format_csv, "table": format_table}
    click.echo(formatter.get(fmt, format_table)(devs))


def _run_watch(fmt, **filters):
    """Stream hotplug events to stdout."""
    import json as json_mod

    from listusb import watch
    from listusb.filters import filter_devices

    active_filters = {k: v for k, v in filters.items() if v is not None}

    click.echo("Watching for USB events... (Ctrl+C to stop)")
    try:
        for event in watch():
            if active_filters and not filter_devices(
                [event.device], **active_filters
            ):
                continue
            if fmt == "json":
                click.echo(
                    json_mod.dumps(
                        {"action": event.action, "device": event.device.to_dict()}
                    )
                )
            else:
                click.echo(
                    f"[{event.action.upper()}] {event.device.path} - {event.device.serial}"
                )
    except KeyboardInterrupt:
        click.echo("\nStopped.")
