"""Typed client for Zellenradschleuse devices."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional
import json

from ..base import BaseMetexonDevice
from .constants import (
    DEVICE_TYPE_UUID,
    SYSTEM_STATE_UUID,
    BLOWER_PID_UUID,
    WIFI_UUID,
    OTA_UUID,
    MANUAL_CONTROL_UUID,
)
from .structures import SystemState, ManualControl, BlowerPID, RGB

class ZellenradschleuseClient(BaseMetexonDevice):
    """Client with typed return values.

    Can be used either with context manager or explicit connect()/disconnect().
    """

    # ---- Typed sync API ----
    def device_type(self) -> str:
        data = self._run(self.client.read_gatt_char(DEVICE_TYPE_UUID))
        return data.decode(errors='replace')

    def read_system_state(self) -> SystemState:
        data = self._run(self.client.read_gatt_char(SYSTEM_STATE_UUID))
        return SystemState.from_bytes(data)

    def write_system_state(self, value: SystemState) -> None:
        self._run(self.client.write_gatt_char(SYSTEM_STATE_UUID, value.to_bytes()))

    def read_blower_pid(self) -> BlowerPID:
        data = self._run(self.client.read_gatt_char(BLOWER_PID_UUID))
        return BlowerPID.from_bytes(data)

    def write_blower_pid(self, value: BlowerPID) -> None:
        self._run(self.client.write_gatt_char(BLOWER_PID_UUID, value.to_bytes()))

    def read_manual_control(self) -> ManualControl:
        data = self._run(self.client.read_gatt_char(MANUAL_CONTROL_UUID))
        return ManualControl.from_bytes(data)

    def write_manual_control(self, value: ManualControl) -> None:
        self._run(self.client.write_gatt_char(MANUAL_CONTROL_UUID, value.to_bytes()))

    def read_rgb_led(self) -> List[tuple[int,int,int]]:
        # RGB is part of the SystemState structure; read and extract it there.
        ss = self.read_system_state()
        return [c.to_tuple() for c in ss.rgb]

    def write_rgb_led(self, colors: Iterable[Iterable[int]]) -> None:
        # To update the RGB LEDs we modify the SystemState.rgb field and write
        # the whole SystemState back. This matches firmware behaviour where the
        # LEDs are part of the system state structure.
        ss = self.read_system_state()
        rgb_objs = []
        for c in colors:
            r, g, b = list(c)
            rgb_objs.append(RGB(r, g, b))
        ss.rgb = rgb_objs
        self.write_system_state(ss)

    def wifi_status(self) -> Dict[str, Any]:
        data = self._run(self.client.read_gatt_char(WIFI_UUID))
        try:
            return json.loads(data.decode())
        except json.JSONDecodeError:
            return {"raw": data.decode(errors='replace')}

    def set_wifi(self, ssid: Optional[str] = None, password: Optional[str] = None) -> None:
        obj: Dict[str, Any] = {}
        if ssid is not None:
            obj['ssid'] = ssid
        if password is not None:
            obj['password'] = password
        self._run(self.client.write_gatt_char(WIFI_UUID, json.dumps(obj).encode()))

    def start_ota(self, url: str) -> None:
        self._run(self.client.write_gatt_char(OTA_UUID, url.encode()))

__all__ = ["ZellenradschleuseClient"]
