"""Backward-compatible high-level client.

This module originally exposed `Zellenradschleuse` with dict-based helpers.
It now wraps the typed `ZellenradschleuseClient` in
`metexon.zellenradschleuse.client` for backwards compatibility.

Prefer importing `ZellenradschleuseClient` from
`metexon.zellenradschleuse` for typed usage.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Iterable

from bleak import BleakClient

from .constants import (
    DEVICE_TYPE_UUID,
    SYSTEM_STATE_UUID,
)
from . import structures as legacy_structs
from .zellenradschleuse.client import ZellenradschleuseClient as _TypedClient
from .loop_thread import AsyncLoopThread

class Zellenradschleuse:
    """High-level convenience wrapper for a Metexon device.

    Example:
        from metexon import Zellenradschleuse
        with Zellenradschleuse(mac="AA:BB:CC:DD:EE:FF") as zr:
            print(zr.device_type())
            state = zr.system_state()
            print(state)
    """
    def __init__(self, mac: str, timeout: float = 10.0) -> None:
        self._typed = _TypedClient(mac, timeout=timeout)
        self.address = mac
        self.timeout = timeout
        self._loop_thread: Optional[AsyncLoopThread] = None  # retained for minimal changes
        self._client: Optional[BleakClient] = None

    # ------------- Context management -------------
    def __enter__(self) -> 'Zellenradschleuse':
        self._typed.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self._typed.disconnect()

    # ------------- Async connect/disconnect -------------
    async def _connect(self) -> None:
        # Deprecated path not used; kept for compatibility if someone calls internal async.
        self._client = BleakClient(self.address, timeout=self.timeout)
        await self._client.__aenter__()

    async def _disconnect(self) -> None:
        if self._client is not None:
            await self._client.__aexit__(None, None, None)
            self._client = None

    # ------------- Internal helpers -------------
    @property
    def client(self) -> BleakClient:
        if not self._client:
            raise RuntimeError("Not connected")
        return self._client

    def _run(self, coro):  # helper bridging
        if not self._loop_thread:
            raise RuntimeError("Loop thread not running")
        return self._loop_thread.run(coro)

    # ------------- Public API (sync wrappers) -------------
    def device_type(self) -> str:
        return self._typed.device_type()

    def system_state(self) -> Dict[str, Any]:
        return self._typed.read_system_state().to_json()

    def set_system_state(self, state: Dict[str, Any]) -> None:
        # Write if firmware supports writing this characteristic (future-proof)
        # Convert using legacy struct then rebuild typed from bytes to avoid type mismatch
        legacy = legacy_structs.SystemState.from_json(state)
        # Reinterpret bytes with typed class
        from .zellenradschleuse.structures import SystemState as _TSystemState
        self._typed.write_system_state(_TSystemState.from_bytes(legacy.to_bytes()))

    def rgb_led(self) -> List[tuple[int, int, int]]:
        return self._typed.read_rgb_led()

    def set_rgb_led(self, colors: Iterable[Iterable[int]]) -> None:
        self._typed.write_rgb_led(colors)

    def blower_pid(self) -> Dict[str, Any]:
        return self._typed.read_blower_pid().to_json()

    def set_blower_pid(self, d: Dict[str, Any]) -> None:
        legacy = legacy_structs.BlowerPID.from_json(d)
        from .zellenradschleuse.structures import BlowerPID as _TBlowerPID
        self._typed.write_blower_pid(_TBlowerPID.from_bytes(legacy.to_bytes()))

    def manual_control(self) -> Dict[str, Any]:
        return self._typed.read_manual_control().to_json()

    def set_manual_control(self, d: Dict[str, Any]) -> None:
        legacy = legacy_structs.ManualControl.from_json(d)
        from .zellenradschleuse.structures import ManualControl as _TManualControl
        self._typed.write_manual_control(_TManualControl.from_bytes(legacy.to_bytes()))

    def wifi_status(self) -> Dict[str, Any]:
        return self._typed.wifi_status()

    def set_wifi(self, ssid: Optional[str] = None, password: Optional[str] = None) -> None:
        self._typed.set_wifi(ssid=ssid, password=password)

    def start_ota(self, url: str) -> None:
        self._typed.start_ota(url)

    # ------------- Async versions (optional external use) -------------
    async def adevice_type(self) -> str:
        data = await self.client.read_gatt_char(DEVICE_TYPE_UUID)
        return data.decode(errors='replace')

    async def asystem_state(self) -> legacy_structs.SystemState:
        data = await self.client.read_gatt_char(SYSTEM_STATE_UUID)
        return legacy_structs.SystemState.from_bytes(data)

    async def aset_system_state(self, state: legacy_structs.SystemState) -> None:
        await self.client.write_gatt_char(SYSTEM_STATE_UUID, state.to_bytes())

    # Additional async methods could mirror sync ones if needed.

__all__ = ["Zellenradschleuse"]
