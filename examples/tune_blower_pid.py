#!/usr/bin/env python3
"""Example: read and tune blower PID (minimal).

Shows both the typed client (`ZellenradschleuseClient`) and the legacy convenience
client (returns dicts) usage patterns. This is intentionally minimal: discover a
device, read PID, update a single field, and exit.
"""
from metexon import discover_metexon
from metexon.zellenradschleuse import ZellenradschleuseClient

# Quick discovery
found = discover_metexon(timeout=5.0)
if not found:
    raise SystemExit("No Metexon device found")
addr = found[0]["address"]

# Typed client (preferred)
with ZellenradschleuseClient(addr) as c:
    pid = c.read_blower_pid()  # returns dataclass-like object
    print("Current PID:", pid)
    # Example: change only Kp and leave others unchanged
    new_pid_partial = {"kp": pid.kp * 1.1}
    c.write_blower_pid(new_pid_partial)
    print("Wrote partial PID update:", new_pid_partial)

# If you prefer the legacy dict-based helper (from metexon.Zellenradschleuse):
try:
    from metexon import Zellenradschleuse
except Exception:
    Zellenradschleuse = None

if Zellenradschleuse:
    DEVICE_MAC = addr
    with Zellenradschleuse(mac=DEVICE_MAC) as zr:
        pid_dict = zr.blower_pid()  # returns dict
        print("Legacy PID (dict):", pid_dict)
        # Set multiple attributes at once (partial update)
        zr.set_blower_pid({"kp": pid_dict["kp"] + 0.1, "ki": pid_dict["ki"]})
        print("Legacy partial update written")
