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

### Basic Usage (typed client)

Use the typed `ZellenradschleuseClient` for structured dataclasses and helper
functions. This example shows reading system state and blower PID, and doing a
partial PID update using the provided helpers.

```python
from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient
from metexon.zellenradschleuse.update_helpers import partial_blower_pid

# Discover a device (5s timeout)
found = discover_metexon(timeout=5.0)
if not found:
	raise SystemExit("No Metexon device found")
addr = found[0]["address"]

with ZellenradschleuseClient(addr) as zr:
	print("Device type:", zr.device_type())

	# Typed dataclass representing system state
	ss = zr.read_system_state()
	print("System state:", ss.to_json())

	# Read typed BlowerPID dataclass
	pid = zr.read_blower_pid()
	print("Blower PID:", pid)

	# Apply a partial update: change Kp only, keep other fields unchanged
	partial = partial_blower_pid(kp=pid.kp * 1.1)
	zr.write_blower_pid(partial)
	print("Wrote partial PID update:", partial)

	# Set RGB LEDs using the typed helper
	zr.set_rgb_led([(255, 0, 0), (0, 0, 255)])

	# Manual control example using typed structure helper
	zr.write_manual_control({"blower_rpm": 1200.0, "feeder_seconds": 5.0, "enable_getriebemotor_nvs": 1})
```

### Returned Data Structures

Methods like `system_state()`, `blower_pid()`, and `manual_control()` return ordinary dict objects suitable for JSON serialization. All binary packing / unpacking and sentinel defaults are handled for you.

### Async Usage

Async access to the typed client is available via the `metexon.zellenradschleuse`
async client. Example using the async typed client:

```python
import asyncio
from metexon.zellenradschleuse.client import ZellenradschleuseClient as AsyncClient

async def main():
	c = AsyncClient("AA:BB:CC:DD:EE:FF")
	await c._connect()
	try:
		print(await c.adevice_type())
		ss = await c.asystem_state()
		print(ss.to_json())
	finally:
		await c._disconnect()

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

Prefer the typed `ZellenradschleuseClient` for new code. The typed client
returns dataclasses with `.to_json()` helpers and accepts typed partial-update
helpers (e.g. `partial_blower_pid`).


- UUID conversion uses the little-endian byte order provided by the firmware macros.
- Writing characteristics that the firmware currently treats as read-only will typically be ignored but is implemented for future compatibility.

# METEXON-BLE
Python library for METEXON supported BLE devices
