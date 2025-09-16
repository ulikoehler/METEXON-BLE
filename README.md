## Metexon BLE Python Client

This repository now contains a Python package `metexon` that provides a high-level, synchronous API (backed by `bleak`) to interact with Metexon BLE devices ("Zellenradschleuse").

### Features

- Automatic conversion of packed binary firmware structs to Python dict / JSON:
  - System state (`SystemStateBinary`)
  - Manual control (`ManualControlBinary`)
  - Blower PID parameters (`BlowerPIDBinary`)
- Read / write helper methods for all relevant characteristics (device type, RGB LEDs, WiFi config, OTA trigger, manual control, PID tuning)
- Simple context manager for connection lifecycle
- Async versions of selected methods for advanced users

### Install (editable from this repo)

```bash
pip install -e .
```

### Basic Usage

```python
from metexon import Zellenradschleuse

DEVICE_MAC = "AA:BB:CC:DD:EE:FF"  # replace with your device

with Zellenradschleuse(mac=DEVICE_MAC) as zr:
	print("Device type:", zr.device_type())

	state = zr.system_state()  # returns dict representing SystemStateBinary
	print("System state:", state)

	# Update (example: change LED colors) using dedicated helper
	zr.set_rgb_led([(255, 0, 0), (0, 0, 255)])

	# Read PID
	pid = zr.blower_pid()
	print("PID:", pid)

	# Write partial PID update (NaN / sentinel semantics handled firmware-side)
	zr.set_blower_pid({"kp": 1.2, "ki": 0.05, "kd": 0.01})

	# Trigger OTA update
	# zr.start_ota("https://example.com/firmware.bin")

	# WiFi configuration
	wifi = zr.wifi_status()
	print("WiFi:", wifi)
	# zr.set_wifi(ssid="MySSID", password="secret")

	# Manual control example: run blower at 1200 rpm for 5 seconds feeder
	zr.set_manual_control({
		"blower_rpm": 1200.0,
		"feeder_seconds": 5.0,
		"enable_getriebemotor_nvs": 1,
	})
```

### Returned Data Structures

Methods like `system_state()`, `blower_pid()`, and `manual_control()` return ordinary dict objects suitable for JSON serialization. All binary packing / unpacking and sentinel defaults are handled for you.

### Async Usage

If you prefer to manage your own asyncio loop:

```python
import asyncio
from bleak import BleakClient
from metexon.client import Zellenradschleuse

async def main():
	zr = Zellenradschleuse(mac="AA:BB:CC:DD:EE:FF")
	await zr._connect()  # internal; you can also adapt pattern to expose a public async enter
	try:
		print(await zr.adevice_type())
		ss = await zr.asystem_state()
		print(ss.to_json())
	finally:
		await zr._disconnect()

asyncio.run(main())
```

### Development

Run serialization tests (after installing dev dependencies if added):

```bash
pytest -k structures
```

### Notes
-## Typed API (Zellenradschleuse)

For future expansion (other Metexon systems), the Zellenradschleuse specific
structures and a typed client were moved into a dedicated namespace
`metexon.zellenradschleuse`.

```python
from metexon.zellenradschleuse import ZellenradschleuseClient

client = ZellenradschleuseClient("AA:BB:CC:DD:EE:FF")
client.connect()
try:
	ss = client.read_system_state()  # returns SystemState dataclass
	print(ss)
	pid = client.read_blower_pid()
	print(pid.kp, pid.ki, pid.kd)
finally:
	client.disconnect()

# Or context manager:
with ZellenradschleuseClient("AA:BB:CC:DD:EE:FF") as c:
	print(c.device_type())
	print(c.read_system_state())
```

Legacy import `from metexon import Zellenradschleuse` still works but returns
dict structures. Prefer the typed client for new code.


- UUID conversion uses the little-endian byte order provided by the firmware macros.
- Writing characteristics that the firmware currently treats as read-only will typically be ignored but is implemented for future compatibility.

# METEXON-BLE
Python library for METEXON supported BLE devices
