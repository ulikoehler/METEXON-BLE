"""Basic example: discover, connect, read system state, update RGB LED, read back.

Run: python examples/zellenradschleuse_basic.py
"""
from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient
from metexon.zellenradschleuse.update_helpers import partial_manual_control

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

    # Example partial manual control update (set feeder for 2s) leaving others unchanged
    mc = partial_manual_control(feeder_seconds=2.0)
    dev.write_manual_control(mc)
    print("Sent manual control request (feeder_seconds=2.0)")

    # Change LEDs: red then blue
    dev.write_rgb_led([(255,0,0), (0,0,255)])
    print("Updated LEDs to red & blue")

    # Re-read system state (may reflect changes depending on firmware refresh timing)
    updated = dev.read_system_state()
    print("Updated system state:", updated.to_json())

print("Done.")
