"""Utility to run an asyncio event loop in a background thread.

Allows providing synchronous wrapper methods that internally run coroutines.
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any, Coroutine, TypeVar, Callable
from concurrent.futures import Future

T = TypeVar('T')

class AsyncLoopThread:
    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._started = threading.Event()
        self._closed = False
        self._thread.start()
        self._started.wait()

    def _run(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._started.set()
        self._loop.run_forever()

    def run(self, coro: Coroutine[Any, Any, T]) -> T:
        if self._closed:
            raise RuntimeError("Loop thread closed")
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result()

    def create_task(self, coro: Coroutine[Any, Any, Any]) -> Future:
        if self._closed:
            raise RuntimeError("Loop thread closed")
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        return self.run(self._call(func, *args, **kwargs))

    async def _shutdown(self) -> None:
        tasks = [t for t in asyncio.all_tasks(loop=self._loop) if not t.done()]
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._loop.stop()

    async def _call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        return func(*args, **kwargs)

    def close(self) -> None:
        if self._closed:
            return
        try:
            asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop).result(timeout=2)
        finally:
            self._closed = True

__all__ = ["AsyncLoopThread"]
