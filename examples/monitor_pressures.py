#!/usr/bin/env python3
"""Continuously read system state and print aligned pressure columns.

Run: python examples/monitor_pressures.py
"""
import time
from metexon import discover_metexon, adiscover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient

# Discover a device (quick scan). Prefer sync helper; callers that already run an
# event loop should call `adiscover_metexon` directly. For convenience we try
# to detect a running loop and fall back to the async function when needed.
try:
    # Prefer the synchronous helper for scripts. If this raises because an
    # event loop is already running, the user should call
    # `await adiscover_metexon(...)` from their async context instead.
    found = discover_metexon(timeout=5.0)
except RuntimeError as exc:
    raise SystemExit(
        "discover_metexon cannot be used here because an event loop is running; "
        "call adiscover_metexon from an async context instead: `found = await adiscover_metexon(...)`"
    )

if not found:
    print("No Metexon devices found.")
    raise SystemExit(1)

addr = found[0]['address']
print(f"Using device {found[0]['name']} @ {addr}\n")

# Print header with fixed column widths
print(f"{'Timestamp':<20} {'Pressure 1 (Pa)':>15} {'Pressure 2 (Pa)':>15}")
print('-' * 52)

try:
    with ZellenradschleuseClient(addr) as dev:
        while True:
            ss = dev.read_system_state()
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            p1 = ss.pressure1
            p2 = ss.pressure2
            # Align columns: timestamp left, pressures right-aligned with 6 decimals
            print(f"{ts:<20} {p1:15.6f} {p2:15.6f}")
            # OPTIONAL: Delay between readings
            # time.sleep(1.0)
except KeyboardInterrupt:
    print('\nStopped by user')

print('Done')
