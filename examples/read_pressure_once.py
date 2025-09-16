#!/usr/bin/env python3
"""Minimal inline example: discover, read pressures once, print, exit."""
from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient

# Find devices
found = discover_metexon(timeout=5.0)
if not found:
    raise SystemExit("No Metexon device found")
addr = found[0]["address"]

# Read pressure once
with ZellenradschleuseClient(addr) as dev:
    ss = dev.read_system_state()
    print(f"Pressure1: {ss.pressure1:.6f} Pa")
    print(f"Pressure2: {ss.pressure2:.6f} Pa")
