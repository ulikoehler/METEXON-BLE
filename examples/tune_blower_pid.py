#!/usr/bin/env python3
"""Example: read and tune blower PID (minimal).

Shows both the typed client (`ZellenradschleuseClient`) and the legacy convenience
client (returns dicts) usage patterns. This is intentionally minimal: discover a
device, read PID, update a single field, and exit.
"""
from metexon.discovery import discover_metexon_one
from metexon.zellenradschleuse import ZellenradschleuseClient
from metexon.zellenradschleuse.update_helpers import partial_blower_pid

# Quick discovery
found = discover_metexon_one(timeout=10.0)
if not found:
    raise SystemExit("No Metexon device found")
addr = found["address"]

# Typed client (preferred)
with ZellenradschleuseClient(addr) as c:
    pid = c.read_blower_pid()  # returns dataclass-like object
    print("Current PID:", pid)
    # Example: change only Kp and leave others unchanged. Use helper to create
    # a BlowerPID object with sentinel no-change values for unspecified fields.
    new_pid = partial_blower_pid(kp=pid.kp * 1.1)
    c.write_blower_pid(new_pid)
    print("Wrote partial PID update (typed):", new_pid)
