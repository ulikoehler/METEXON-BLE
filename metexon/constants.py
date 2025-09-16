"""UUID constants for Metexon BLE service and characteristics.

The firmware provides UUIDs using the BLE_UUID128_INIT macro listing bytes
least-significant first (LSB first) as is customary in many embedded BLE
stacks (e.g. NimBLE / ESP-IDF). To obtain the canonical UUID string form
used by Bleak / Python (big-endian groups per RFC 4122), we reverse the
16-byte sequence.

If you ever need to add another characteristic, copy the 16 bytes from the
firmware macro and add them to the mapping below.
"""
from __future__ import annotations

from uuid import UUID


def _uuid_from_le_bytes(byte_list: list[int]) -> UUID:
    """Return canonical UUID from a list of 16 bytes given LSB-first.

    Firmware macro BLE_UUID128_INIT( b0, b1, ... b15 ) lists the raw 128-bit
    value LSB-first. Canonical textual UUID reverses that order.
    """
    if len(byte_list) != 16:
        raise ValueError("UUID byte list must have length 16")
    return UUID(bytes=bytes(reversed(byte_list)))


# Raw byte definitions copied from firmware (BLE_UUID128_INIT order)
_SERVICE_BYTES = [0xAA, 0x85, 0x9E, 0x5F, 0xDD, 0x5A, 0x82, 0x42, 0x81, 0x84, 0xC4, 0xE1, 0x23, 0x5F, 0x35, 0x42]
_DEVICE_TYPE_BYTES = [0xA0, 0xAF, 0x5C, 0xCA, 0xB2, 0x97, 0xDF, 0x4F, 0xBC, 0xC2, 0xFA, 0x6B, 0x78, 0xB7, 0xF7, 0x68]
_SYSTEM_STATE_BYTES = [0x68, 0x87, 0x98, 0x89, 0x0F, 0xFE, 0xAC, 0x4F, 0xAD, 0x0D, 0xF0, 0xDB, 0x24, 0xF6, 0xB1, 0x2F]
_RGB_LED_BYTES = [0x6C, 0xD5, 0xD1, 0x16, 0x9A, 0x35, 0x54, 0x4B, 0xBA, 0xCC, 0x47, 0xF1, 0x94, 0x0F, 0x37, 0x95]
_BLOWER_PID_BYTES = [0x4C, 0x38, 0x61, 0x23, 0x01, 0xBB, 0xA4, 0x41, 0x8F, 0x1B, 0x41, 0x8F, 0x95, 0x13, 0xC0, 0x60]
_WIFI_BYTES = [0xBD, 0xDA, 0x5D, 0x96, 0xF0, 0xF6, 0x7F, 0x45, 0x9C, 0x6D, 0x59, 0xF5, 0xB4, 0x6C, 0x77, 0x07]
_OTA_BYTES = [0x3E, 0x2D, 0x88, 0xB7, 0xEA, 0xED, 0x19, 0x43, 0x91, 0xB8, 0xD2, 0x04, 0x5F, 0x85, 0xD1, 0x2C]
_MANUAL_CONTROL_BYTES = [0x7B, 0xC1, 0x42, 0x5E, 0x11, 0xAA, 0x4D, 0x49, 0xA7, 0x77, 0xC5, 0x31, 0x9F, 0x42, 0xB3, 0x56]


METEXON_SERVICE_UUID = _uuid_from_le_bytes(_SERVICE_BYTES)
DEVICE_TYPE_UUID = _uuid_from_le_bytes(_DEVICE_TYPE_BYTES)
SYSTEM_STATE_UUID = _uuid_from_le_bytes(_SYSTEM_STATE_BYTES)
RGB_LED_UUID = _uuid_from_le_bytes(_RGB_LED_BYTES)
BLOWER_PID_UUID = _uuid_from_le_bytes(_BLOWER_PID_BYTES)
WIFI_UUID = _uuid_from_le_bytes(_WIFI_BYTES)
OTA_UUID = _uuid_from_le_bytes(_OTA_BYTES)
MANUAL_CONTROL_UUID = _uuid_from_le_bytes(_MANUAL_CONTROL_BYTES)

ALL_UUIDS = {
    "service": METEXON_SERVICE_UUID,
    "device_type": DEVICE_TYPE_UUID,
    "system_state": SYSTEM_STATE_UUID,
    "rgb_led": RGB_LED_UUID,
    "blower_pid": BLOWER_PID_UUID,
    "wifi": WIFI_UUID,
    "ota": OTA_UUID,
    "manual_control": MANUAL_CONTROL_UUID,
}

__all__ = [
    "METEXON_SERVICE_UUID",
    "DEVICE_TYPE_UUID",
    "SYSTEM_STATE_UUID",
    "RGB_LED_UUID",
    "BLOWER_PID_UUID",
    "WIFI_UUID",
    "OTA_UUID",
    "MANUAL_CONTROL_UUID",
    "ALL_UUIDS",
]
