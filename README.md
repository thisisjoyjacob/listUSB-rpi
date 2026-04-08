# listusb-rpi

List and monitor USB devices on Raspberry Pi and Linux. Provides both a **Python API** for use in your projects and a **CLI tool** for the terminal.

## Install

```bash
pip install listusb-rpi
```

For full functionality (recommended on Raspberry Pi):

```bash
sudo apt install libudev-dev
pip install listusb-rpi[udev]
```

## Python API

```python
from listusb import devices, find_device

# List all USB devices
for dev in devices():
    print(dev.path, dev.vendor, dev.serial)

# Filter devices
serial_devices = devices(subsystem="tty")
ftdi_devices = devices(vendor="FTDI")
specific = devices(vid="0403", pid="6001")

# Find a specific device
arduino = find_device(vendor="Arduino")
if arduino:
    print(f"Arduino found at {arduino.path}")
```

### USBDevice fields

| Field | Description | Example |
|-------|-------------|---------|
| `path` | Device path | `/dev/ttyUSB0` |
| `name` | Device model name | `FT232R_USB_UART` |
| `serial` | Serial identifier | `FTDI_FT232R_A50285BI` |
| `vendor` | Vendor name | `Future Technology Devices International` |
| `product` | Product name | `FT232 Serial (UART) IC` |
| `vid` | Vendor ID | `0403` |
| `pid` | Product ID | `6001` |
| `speed` | USB speed (Mbps) | `12` |
| `driver` | Kernel driver | `ftdi_sio` |
| `subsystem` | Linux subsystem | `tty` |

### Watch for hotplug events

```python
from listusb import watch

for event in watch():
    print(f"[{event.action}] {event.device.path} - {event.device.serial}")
```

Requires pyudev: `pip install listusb-rpi[udev]`

## CLI Usage

```bash
# List all USB devices (table format)
listusb-rpi

# Output as JSON
listusb-rpi --json

# Output as CSV
listusb-rpi --csv

# Filter by vendor
listusb-rpi --vendor FTDI

# Filter by type (aliases: serial, storage, camera, audio, network)
listusb-rpi --type serial

# Filter by vendor/product ID
listusb-rpi --vid 0403 --pid 6001

# Watch for USB plug/unplug events
listusb-rpi --watch

# Watch with JSON output
listusb-rpi --watch --json
```

## Optional dependencies

```bash
pip install listusb-rpi[udev]      # pyudev for full device info + watch mode
pip install listusb-rpi[mqtt]      # MQTT publishing for IoT
pip install listusb-rpi[webhook]   # Webhook notifications
pip install listusb-rpi[all]       # Everything
```

## Requirements

- Python >= 3.9
- Linux (Raspberry Pi OS, Ubuntu, Debian, etc.)
- `libudev-dev` for pyudev support: `sudo apt install libudev-dev`

## License

Apache-2.0
