"""Device discovery utilities for Metexon BLE devices."""
from __future__ import annotations

from typing import List
from bleak import BleakScanner
from .constants import METEXON_SERVICE_UUID

__all__ = ["discover_metexon", "adiscover_metexon"]
__all__ += ["discover_metexon_one", "adiscover_metexon_one"]

async def adiscover_metexon(timeout: float = 5.0, filter_by: str = "name") -> List[dict]:
    """Async discover Metexon devices.

    filter_by controls which matching strategy to use:
      - "name": include devices whose advertised name contains "METEXON" (case-insensitive). This is the default.
      - "service": include devices that advertise the Metexon primary service UUID.

    Returns a list of dictionaries with keys: address, name, rssi.
    """
    devices = await BleakScanner.discover(timeout=timeout)
    result = []
    svc_str = str(METEXON_SERVICE_UUID)
    for d in devices:
        name = (d.name or "")
        metadata = getattr(d, 'metadata', {}) or {}
        uuids = metadata.get('uuids') or []
        match = False
        if filter_by == "name":
            if "metexon" in name.lower():
                match = True
        elif filter_by == "service":
            if svc_str.lower() in [u.lower() for u in uuids]:
                match = True
        else:
            raise ValueError(f"Unknown filter_by value: {filter_by!r}; expected 'name' or 'service'")

        if match:
            result.append({
                'address': d.address,
                'name': d.name,
                'rssi': getattr(d, 'rssi', None),
            })
    return result


async def adiscover_metexon_one(timeout: float = 10.0, filter_by: str = "name") -> dict | None:
    """Async discover a single Metexon device and stop as soon as one is found.

    Returns a dict with keys: address, name, rssi, or None if no device was found within timeout.
    """
    svc_str = str(METEXON_SERVICE_UUID).lower()

    # Repeated short discovers are used instead of a callback-based scanner so
    # this works across bleak versions and avoids relying on scanner internals.
    import asyncio as _asyncio
    import time as _time

    end_time = _time.time() + float(timeout)
    scan_interval = min(1.0, float(timeout) or 1.0)
    if scan_interval <= 0:
        scan_interval = 0.5

    while _time.time() <= end_time:
        remaining = end_time - _time.time()
        this_try = min(scan_interval, remaining) if remaining > 0 else 0
        try:
            devices = await BleakScanner.discover(timeout=this_try)
        except Exception:
            # If discover fails for any reason, short-circuit with None
            return None

        for d in devices:
            name = (d.name or "")
            metadata = getattr(d, 'metadata', {}) or {}
            uuids = metadata.get('uuids') or []
            match = False
            if filter_by == "name":
                if "metexon" in name.lower():
                    match = True
            elif filter_by == "service":
                if svc_str in [u.lower() for u in uuids]:
                    match = True
            else:
                raise ValueError(f"Unknown filter_by value: {filter_by!r}; expected 'name' or 'service'")

            if match:
                return {
                    'address': d.address,
                    'name': d.name,
                    'rssi': getattr(d, 'rssi', None),
                }

        # yield to the event loop briefly before next discover
        try:
            await _asyncio.sleep(0)
        except Exception:
            pass

    return None

def discover_metexon(timeout: float = 10.0, filter_by: str = "name") -> List[dict]:
    """Synchronous wrapper for `adiscover_metexon`.

    See `filter_by` semantics in `adiscover_metexon`.
    """
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Caller already in event loop; user should call adiscover_metexon directly.
        raise RuntimeError("discover_metexon cannot run inside an existing event loop; use adiscover_metexon")
    return asyncio.run(adiscover_metexon(timeout=timeout, filter_by=filter_by))


def discover_metexon_one(timeout: float = 10.0, filter_by: str = "name") -> dict | None:
    """Synchronous wrapper for `adiscover_metexon_one`.

    Returns a dict for the first found device or None if none found within timeout.
    """
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        raise RuntimeError("discover_metexon_one cannot run inside an existing event loop; use adiscover_metexon_one")
    return asyncio.run(adiscover_metexon_one(timeout=timeout, filter_by=filter_by))
