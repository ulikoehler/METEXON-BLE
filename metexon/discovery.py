"""Device discovery utilities for Metexon BLE devices."""
from __future__ import annotations

from typing import List
from bleak import BleakScanner
from .constants import METEXON_SERVICE_UUID

__all__ = ["discover_metexon", "adiscover_metexon"]

async def adiscover_metexon(timeout: float = 5.0) -> List[dict]:
    """Async discover devices advertising the Metexon primary service.

    Returns a list of dictionaries with keys: address, name, rssi.
    """
    devices = await BleakScanner.discover(timeout=timeout)
    result = []
    svc_str = str(METEXON_SERVICE_UUID)
    for d in devices:
        metadata = getattr(d, 'metadata', {}) or {}
        uuids = metadata.get('uuids') or []
        if svc_str.lower() in [u.lower() for u in uuids]:
            result.append({
                'address': d.address,
                'name': d.name,
                'rssi': getattr(d, 'rssi', None),
            })
    return result

def discover_metexon(timeout: float = 5.0) -> List[dict]:
    """Synchronous wrapper for `adiscover_metexon`."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Caller already in event loop; user should call adiscover_metexon directly.
        raise RuntimeError("discover_metexon cannot run inside an existing event loop; use adiscover_metexon")
    return asyncio.run(adiscover_metexon(timeout=timeout))
