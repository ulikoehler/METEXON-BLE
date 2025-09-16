"""Device discovery utilities for Metexon BLE devices."""
from __future__ import annotations

from typing import List
from bleak import BleakScanner
from .constants import METEXON_SERVICE_UUID

__all__ = ["discover_metexon", "adiscover_metexon"]

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
