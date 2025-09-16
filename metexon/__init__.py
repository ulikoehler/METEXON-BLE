"""Metexon BLE high-level client library.

Legacy dict-based client: :class:`Zellenradschleuse` (kept for compatibility).
Typed device-specific client: :class:`ZellenradschleuseClient` available under
`metexon.zellenradschleuse`.

Basic example (typed):

    from metexon.zellenradschleuse import ZellenradschleuseClient
    zr = ZellenradschleuseClient("AA:BB:CC:DD:EE:FF")
    zr.connect()
    try:
        print(zr.device_type())
        print(zr.read_system_state())
    finally:
        zr.disconnect()
"""
from .client import Zellenradschleuse  # noqa: F401
from .zellenradschleuse import ZellenradschleuseClient  # noqa: F401
from .zellenradschleuse import sentinels as zsentinels  # noqa: F401
from .discovery import discover_metexon, adiscover_metexon  # noqa: F401

__all__ = [
    "Zellenradschleuse",
    "ZellenradschleuseClient",
    "zsentinels",
    "discover_metexon",
    "adiscover_metexon",
]
