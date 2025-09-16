"""Basic example: discover, connect, read system state, update RGB LED, read back.

Run: python examples/zellenradschleuse_basic.py
"""
from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient

# Discover devices
print("Discovering Metexon devices...")
found = discover_metexon(timeout=5.0)
if not found:
    print("No Metexon devices found.")
    raise SystemExit(1)

device_info = found[0]
print("Using device:", device_info)
addr = device_info['address']

# Connect
with ZellenradschleuseClient(addr) as dev:
    print("Device type:", dev.device_type())
    state = dev.read_system_state()
    print("Initial system state:", state.to_json())

    # Change LEDs: green then blue
    dev.write_rgb_led([(0,255,0), (0,0,255)])
    print("Updated LEDs to green & blue")

    # Re-read system state (may reflect changes depending on firmware refresh timing)
    updated = dev.read_system_state()
    print("Updated system state:", updated.to_json())

print("Done.")
