#!/usr/bin/env python3
"""List available stream parameters and print live binary BLE parameter frames.

Usage:
    python examples/stream_parameters.py
"""
from __future__ import annotations

import time
from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient


def main() -> None:
    found = discover_metexon(timeout=10.0)
    if not found:
        raise SystemExit("No Metexon device found")

    dev = found[0]
    address = dev["address"]
    print(f"Using {dev.get('name', 'Metexon')} @ {address}")

    with ZellenradschleuseClient(address) as zr:
        entries = zr.parameter_stream_list()
        print(f"\nAvailable stream parameters: {len(entries)}")
        for e in entries:
            print(f"  {int(e['id']):3d}  {e['name']:<24} {e['type']:<5}  {e['desc']}")

        selected_ids = [102, 103, 104, 106, 107, 108, 109, 110, 113, 115, 118, 122, 126, 139]
        status = zr.parameter_stream_start(interval_ms=150, ids=selected_ids)
        print(f"\nStream started: running={status.get('running')} interval_ms={status.get('interval_ms')}")

        print("\nTimestamp(us)      ID   Value")
        print("-" * 52)
        t_end = time.monotonic() + 20.0
        while time.monotonic() < t_end:
            frame = zr.read_parameter_stream_frame()
            if frame is None:
                time.sleep(0.03)
                continue
            print(f"{frame.timestamp_us:14d}  {frame.parameter_id:3d}  {frame.value}")

        zr.parameter_stream_stop()
        print("\nStream stopped")


if __name__ == "__main__":
    main()
