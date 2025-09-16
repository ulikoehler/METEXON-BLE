"""Shared base class for Metexon BLE devices.

Encapsulates connection management and optional context manager support.
"""
from __future__ import annotations

from typing import Optional, Any, Coroutine, TypeVar
from bleak import BleakClient

from .loop_thread import AsyncLoopThread

T = TypeVar('T')

class BaseMetexonDevice:
    def __init__(self, address: str, timeout: float = 10.0, auto_loop: bool = True) -> None:
        self.address = address
        self.timeout = timeout
        self._client: Optional[BleakClient] = None
        self._loop_thread: Optional[AsyncLoopThread] = None
        self._auto_loop = auto_loop

    # -------- public sync API --------
    def connect(self) -> None:
        if self._client:
            return
        if self._auto_loop and not self._loop_thread:
            self._loop_thread = AsyncLoopThread()
        self._run(self._aconnect())

    def disconnect(self) -> None:
        if self._client:
            self._run(self._adisconnect())
        if self._loop_thread:
            self._loop_thread.close()
            self._loop_thread = None

    # -------- internal async --------
    async def _aconnect(self) -> None:
        self._client = BleakClient(self.address, timeout=self.timeout)
        await self._client.__aenter__()

    async def _adisconnect(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    # -------- helpers --------
    def _run(self, coro: Coroutine[Any, Any, T]) -> T:
        if not self._loop_thread:
            raise RuntimeError("No loop thread (auto_loop=False?)")
        return self._loop_thread.run(coro)

    @property
    def client(self) -> BleakClient:
        if not self._client:
            raise RuntimeError("Not connected")
        return self._client

    # -------- context manager --------
    def __enter__(self):  # type: ignore[override]
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[override]
        self.disconnect()
        return False
