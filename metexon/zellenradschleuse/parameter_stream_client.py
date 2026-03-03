"""Parameter stream BLE access for Zellenradschleuse devices."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional
import json
import struct
import time

from .constants import (
    PARAM_STREAM_LIST_UUID,
    PARAM_STREAM_CONTROL_UUID,
    PARAM_STREAM_DATA_UUID,
)


_FRAME_STRUCT = struct.Struct('<QHBB16s')


@dataclass
class ParameterStreamFrame:
    timestamp_us: int
    parameter_id: int
    value_type: int
    value_size: int
    value_bytes: bytes
    value: Any

    @classmethod
    def from_bytes(cls, data: bytes) -> "ParameterStreamFrame":
        if len(data) < _FRAME_STRUCT.size:
            raise ValueError(f"ParameterStreamFrame expected {_FRAME_STRUCT.size} bytes, got {len(data)}")
        timestamp_us, parameter_id, value_type, value_size, raw = _FRAME_STRUCT.unpack(data[:_FRAME_STRUCT.size])
        payload = raw[:value_size]
        value = _decode_value(value_type, payload)
        return cls(
            timestamp_us=timestamp_us,
            parameter_id=parameter_id,
            value_type=value_type,
            value_size=value_size,
            value_bytes=payload,
            value=value,
        )


def _decode_value(value_type: int, payload: bytes) -> Any:
    if value_type == 1 and len(payload) >= 1:
        return struct.unpack('<B', payload[:1])[0]
    if value_type == 2 and len(payload) >= 2:
        return struct.unpack('<H', payload[:2])[0]
    if value_type == 3 and len(payload) >= 4:
        return struct.unpack('<I', payload[:4])[0]
    if value_type == 4 and len(payload) >= 8:
        return struct.unpack('<Q', payload[:8])[0]
    if value_type == 5 and len(payload) >= 4:
        return struct.unpack('<i', payload[:4])[0]
    if value_type == 6 and len(payload) >= 4:
        return struct.unpack('<f', payload[:4])[0]
    if value_type == 7 and len(payload) >= 1:
        return struct.unpack('<B', payload[:1])[0] != 0
    return payload


class ParameterStreamClient:
    """Mixin adding parameter stream list/control/frame operations over BLE."""

    def parameter_stream_list(self: Any) -> List[Dict[str, Any]]:
        all_entries: List[Dict[str, Any]] = []
        offset = 0
        while True:
            cmd = json.dumps({"o": offset}).encode()
            self._run(self.client.write_gatt_char(PARAM_STREAM_LIST_UUID, cmd, response=True))
            raw = self._run(self.client.read_gatt_char(PARAM_STREAM_LIST_UUID))
            page = json.loads(raw.decode())
            entries = page.get("entries", [])
            all_entries.extend(entries)
            if not page.get("more", False):
                break
            offset += len(entries)
        return all_entries

    def parameter_stream_control(self: Any, *, running: Optional[bool] = None,
                                 interval_ms: Optional[int] = None,
                                 ids: Optional[List[int]] = None,
                                 cmd: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if running is not None:
            payload["running"] = bool(running)
        if interval_ms is not None:
            payload["interval_ms"] = int(interval_ms)
        if ids is not None:
            payload["ids"] = [int(v) for v in ids]
        if cmd is not None:
            payload["cmd"] = cmd

        if payload:
            self._run(self.client.write_gatt_char(PARAM_STREAM_CONTROL_UUID, json.dumps(payload).encode(), response=True))
        raw = self._run(self.client.read_gatt_char(PARAM_STREAM_CONTROL_UUID))
        return json.loads(raw.decode())

    def parameter_stream_start(self: Any, *, interval_ms: int = 120, ids: Optional[List[int]] = None) -> Dict[str, Any]:
        return self.parameter_stream_control(running=True, interval_ms=interval_ms, ids=ids, cmd="start")

    def parameter_stream_stop(self: Any) -> Dict[str, Any]:
        return self.parameter_stream_control(running=False, cmd="stop")

    def read_parameter_stream_frame(self: Any) -> Optional[ParameterStreamFrame]:
        raw = self._run(self.client.read_gatt_char(PARAM_STREAM_DATA_UUID))
        if not raw:
            return None
        return ParameterStreamFrame.from_bytes(bytes(raw))

    def iter_parameter_stream_frames(self: Any, *, duration_s: Optional[float] = None,
                                     poll_interval_s: float = 0.05) -> Iterator[ParameterStreamFrame]:
        deadline = None if duration_s is None else (time.monotonic() + duration_s)
        while True:
            if deadline is not None and time.monotonic() >= deadline:
                break
            frame = self.read_parameter_stream_frame()
            if frame is not None:
                yield frame
            if poll_interval_s > 0:
                time.sleep(poll_interval_s)


__all__ = ["ParameterStreamClient", "ParameterStreamFrame"]
