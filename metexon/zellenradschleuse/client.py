"""Typed client for Zellenradschleuse devices."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional
import json

from ..base import BaseMetexonDevice
from .constants import (
    DEVICE_TYPE_UUID,
    SYSTEM_STATE_UUID,
    RGB_LED_UUID,
    BLOWER_PID_UUID,
    WIFI_UUID,
    OTA_UUID,
    MANUAL_CONTROL_UUID,
)
from .structures import SystemState, ManualControl, BlowerPID

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
        data = self._run(self.client.read_gatt_char(RGB_LED_UUID))
        leds: List[tuple[int,int,int]] = []
        for i in range(0, len(data), 3):
            chunk = data[i:i+3]
            if len(chunk) == 3:
                leds.append((chunk[0], chunk[1], chunk[2]))
        return leds

    def write_rgb_led(self, colors: Iterable[Iterable[int]]) -> None:
        flat: List[int] = []
        for c in colors:
            r, g, b = list(c)
            flat.extend([r & 0xFF, g & 0xFF, b & 0xFF])
        self._run(self.client.write_gatt_char(RGB_LED_UUID, bytes(flat)))

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
