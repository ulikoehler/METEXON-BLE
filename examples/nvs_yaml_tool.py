#!/usr/bin/env python3
"""nvs_yaml_tool.py — Backup, document and restore NVS parameters over BLE.

Usage
-----
List all NVS parameters currently on the device::

    python nvs_yaml_tool.py --address AA:BB:CC:DD:EE:FF list

Dump all parameters to a YAML file (with descriptions as comments)::

    python nvs_yaml_tool.py --address AA:BB:CC:DD:EE:FF dump params.yaml

Apply parameters from a YAML file to the device::

    python nvs_yaml_tool.py --address AA:BB:CC:DD:EE:FF apply params.yaml

Read a single parameter::

    python nvs_yaml_tool.py --address AA:BB:CC:DD:EE:FF get serial

Write a single parameter::

    python nvs_yaml_tool.py --address AA:BB:CC:DD:EE:FF set blower_oper_pwm 900

The device BLE address can also be provided via the METEXON_ADDRESS environment
variable to avoid repeating it on every call.

YAML file format
----------------
The YAML file produced by ``dump`` has one key per NVS entry.  Each key maps
to its current value.  Descriptions are included as inline YAML comments so
the file serves as self-documenting configuration::

    # NVS parameters for Zellenradschleuse
    # Device: AA:BB:CC:DD:EE:FF  Dumped: 2026-03-03 12:00:00

    serial: NOSERIAL          # Device serial number (set at manufacturing)
    blower_oper_pwm: 900      # Blower PWM duty cycle (0-1023) while actively feeding
    ...

The ``apply`` command reads this file and writes each key back to the device.
Keys unknown to the device are skipped with a warning.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Ensure the workspace copy of the library is importable when running directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from metexon.zellenradschleuse import ZellenradschleuseClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_yaml_with_comments(entries: List[Dict[str, Any]], address: str) -> str:
    """Render NVS entries as a YAML string with inline description comments.

    Each entry dict must have keys: ``key``, ``value``, ``type``, ``desc``.
    """
    lines: List[str] = [
        "# NVS parameters for Zellenradschleuse",
        f"# Device : {address}",
        f"# Dumped : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Entries: {len(entries)}",
        "#",
        "# Edit the values below, then use --apply to write them back to the device.",
        "# String values must be quoted if they contain special characters.",
        "",
    ]
    for e in entries:
        key   = e["key"]
        value = e["value"]
        desc  = e.get("desc", "")
        typ   = e.get("type", "string")

        # For numeric types that come back as strings, preserve native YAML types
        yaml_value: Any = value
        try:
            if typ == "float":
                yaml_value = float(value)
            elif typ in ("uint16", "uint32", "uint64"):
                yaml_value = int(value)
        except (ValueError, TypeError):
            yaml_value = value

        # Single-line YAML dump of the key and value
        kv = yaml.dump({key: yaml_value}, default_flow_style=False).rstrip()

        # Append description as inline comment
        if desc:
            lines.append(f"{kv}  # {desc}")
        else:
            lines.append(kv)

    lines.append("")  # trailing newline
    return "\n".join(lines)


def _read_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping (got {type(data).__name__})")
    return data


def _print_table(entries: List[Dict[str, Any]]) -> None:
    """Pretty-print entries as a table."""
    col_key  = max((len(e["key"]) for e in entries), default=4)
    col_type = max((len(e.get("type", "")) for e in entries), default=4)
    col_val  = max((len(str(e.get("value", ""))) for e in entries), default=5)

    header = f"{'KEY':<{col_key}}  {'TYPE':<{col_type}}  {'VALUE':<{col_val}}  DESCRIPTION"
    print(header)
    print("-" * len(header))
    for e in entries:
        print(f"{e['key']:<{col_key}}  {e.get('type',''):<{col_type}}  "
              f"{str(e.get('value','')):<{col_val}}  {e.get('desc','')}")


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_list(client: ZellenradschleuseClient, _args: argparse.Namespace) -> None:
    print("Reading NVS entries from device…")
    entries = client.nvs_list()
    _print_table(entries)
    print(f"\nTotal: {len(entries)} entries")


def cmd_dump(client: ZellenradschleuseClient, args: argparse.Namespace) -> None:
    path = args.file
    print(f"Reading NVS entries from device…")
    entries = client.nvs_list()
    yaml_text = _format_yaml_with_comments(entries, args.address)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(yaml_text)
    print(f"Wrote {len(entries)} entries to {path!r}")


def cmd_apply(client: ZellenradschleuseClient, args: argparse.Namespace) -> None:
    path = args.file
    params = _read_yaml(path)
    print(f"Applying {len(params)} parameters from {path!r}…")

    # Fetch existing keys from device to validate
    existing_entries = client.nvs_list(include_values=False)
    known_keys = {e["key"] for e in existing_entries}

    errors: List[str] = []
    skipped: List[str] = []
    written: List[str] = []

    for key, value in params.items():
        if key not in known_keys:
            print(f"  SKIP  {key!r} (key not known to device)")
            skipped.append(key)
            continue
        try:
            client.nvs_set(key, value)
            print(f"  OK    {key} = {value!r}")
            written.append(key)
        except RuntimeError as exc:
            print(f"  ERROR {key}: {exc}", file=sys.stderr)
            errors.append(f"{key}: {exc}")

    print(f"\nSummary: {len(written)} written, {len(skipped)} skipped, {len(errors)} errors")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)


def cmd_get(client: ZellenradschleuseClient, args: argparse.Namespace) -> None:
    entry = client.nvs_get(args.key)
    print(f"{entry['key']}: {entry['value']}  [{entry['type']}]  # {entry['desc']}")


def cmd_set(client: ZellenradschleuseClient, args: argparse.Namespace) -> None:
    client.nvs_set(args.key, args.value)
    print(f"Set {args.key!r} = {args.value!r} — OK")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backup, document and restore Zellenradschleuse NVS parameters over BLE.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--address", "-a",
        default=os.environ.get("METEXON_ADDRESS"),
        help="BLE device address (or set METEXON_ADDRESS env var)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="Print all NVS parameters from device")

    # dump
    p_dump = sub.add_parser("dump", help="Save all NVS parameters to YAML file")
    p_dump.add_argument("file", help="Output YAML file path")

    # apply
    p_apply = sub.add_parser("apply", help="Apply YAML file of parameters to device")
    p_apply.add_argument("file", help="Input YAML file path")

    # get
    p_get = sub.add_parser("get", help="Read a single NVS key from device")
    p_get.add_argument("key", help="NVS key name")

    # set
    p_set = sub.add_parser("set", help="Write a single NVS key to device")
    p_set.add_argument("key",   help="NVS key name")
    p_set.add_argument("value", help="New value (as string; firmware does type conversion)")

    args = parser.parse_args()

    if not args.address:
        parser.error("BLE address required (--address or METEXON_ADDRESS env var)")

    commands = {
        "list":  cmd_list,
        "dump":  cmd_dump,
        "apply": cmd_apply,
        "get":   cmd_get,
        "set":   cmd_set,
    }
    handler = commands[args.command]

    print(f"Connecting to {args.address}…")
    with ZellenradschleuseClient(args.address) as client:
        print("Connected.")
        handler(client, args)


if __name__ == "__main__":
    main()
