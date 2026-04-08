# Changelog

## 0.1.0 (unreleased)

- Initial release
- Python API: `devices()`, `find_device()`, `scan()`, `watch()`
- CLI tool: `listusb-rpi` with `--json`, `--csv`, `--table` output formats
- Device filtering by vendor, vid, pid, type, driver
- Watch mode for hotplug events (`--watch`)
- Friendly type aliases: `--type serial`, `--type storage`, `--type camera`, etc.
- pyudev scanner with sysfs fallback for environments without libudev
- Full test suite (60 tests)
