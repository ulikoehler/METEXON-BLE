#!/usr/bin/env python3
"""Example: initialize client once and never explicitly disconnect.

This shows the sync API where the client is created and left for the
process lifetime. It's useful for long-running applications (daemons,
services) that keep a persistent connection. The underlying
`BaseMetexonDevice` starts an event loop thread automatically and will
clean up on process exit if the Python interpreter shuts down; however,
if you want an explicit graceful shutdown, call `disconnect()`.

Run: python examples/client_no_disconnect.py
"""
from time import sleep

from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient


print("Discovering Metexon devices...")
found = discover_metexon(timeout=5.0)
if not found:
    print("No Metexon devices found.")
    raise SystemExit(1)

device_info = found[0]
addr = device_info["address"]
print(f"Using device: {addr} ({device_info.get('name')})")

# Create the client once and connect. We do not use a `with` block and
# we don't call `disconnect()` later. The client will keep the BLE
# connection and loop thread alive for the life of this process.
client = ZellenradschleuseClient(addr)
client.connect()

try:
    # Read device type and system state periodically in a long-running
    # loop. Replace this with your app's main loop.
    for i in range(10):
        print(f"Iteration {i+1}")
        try:
            print("  Device type:", client.device_type())
            state = client.read_system_state()
            print("  System state:", state.to_json())
        except Exception as e:
            # Handle transient read errors (connection drops, timeouts)
            print("  Read error:", e)

        # Sleep to simulate ongoing work. In real code use a proper
        # event loop or scheduling. Keeping this simple for the example.
        sleep(2.0)

    print("Example finished — leaving client connected.")

    # Note: we intentionally do NOT call client.disconnect() here.
    # If the process exits, resources will be reclaimed by the OS.
    # To shut down cleanly from your application, call client.disconnect().

except KeyboardInterrupt:
    print("Interrupted — you may want to call client.disconnect() to clean up.")
