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


# Raw byte definitions copied from firmware (BLE_UUID128_INIT order) for items
# where a canonical UUID string has not been explicitly supplied. We still
# include the service and RGB LED via byte form (canonical strings were not
# provided), while all other characteristics use the authoritative UUID
# strings published by firmware / documentation below.
_SERVICE_BYTES = [0xAA, 0x85, 0x9E, 0x5F, 0xDD, 0x5A, 0x82, 0x42, 0x81, 0x84, 0xC4, 0xE1, 0x23, 0x5F, 0x35, 0x42]
_RGB_LED_BYTES = [0x6C, 0xD5, 0xD1, 0x16, 0x9A, 0x35, 0x54, 0x4B, 0xBA, 0xCC, 0x47, 0xF1, 0x94, 0x0F, 0x37, 0x95]

# NVS configuration service bytes (generated with generate_bluetooth_uuid.py)
_NVS_SERVICE_BYTES  = [0x1D, 0xA4, 0xCF, 0x47, 0x96, 0xB0, 0xC1, 0x43, 0xB0, 0x19, 0x8B, 0x3E, 0xE6, 0x12, 0x9F, 0x31]
_NVS_LIST_BYTES     = [0x77, 0x64, 0x0A, 0xBD, 0xF9, 0xBE, 0xE1, 0x4E, 0x9C, 0xBD, 0x28, 0x3B, 0x11, 0x2B, 0x96, 0x1B]
_NVS_GET_BYTES      = [0xE4, 0x17, 0xBF, 0x7E, 0x6B, 0x56, 0xFE, 0x40, 0x9A, 0xD1, 0xE9, 0x9B, 0xA1, 0xE3, 0x28, 0x39]
_NVS_SET_BYTES      = [0xFD, 0x35, 0xE9, 0xDB, 0x60, 0xF4, 0x1C, 0x44, 0x9D, 0x3D, 0x2B, 0x7F, 0x2B, 0xC4, 0x4B, 0xD9]

# Parameter stream service bytes (generated with generate_bluetooth_uuid.py)
_PARAM_STREAM_SERVICE_BYTES = [0x22, 0x07, 0x3F, 0x60, 0x75, 0xEA, 0x20, 0x48, 0xA0, 0x9C, 0x9B, 0xD6, 0x0B, 0x56, 0x8C, 0xAD]
_PARAM_STREAM_LIST_BYTES = [0xDE, 0x09, 0x62, 0x04, 0x87, 0x44, 0xE9, 0x49, 0xB7, 0xAE, 0xD9, 0x16, 0x12, 0xF5, 0x88, 0x2B]
_PARAM_STREAM_CONTROL_BYTES = [0x30, 0x24, 0xD6, 0x7D, 0xC7, 0xC8, 0x25, 0x46, 0x9B, 0xC8, 0x23, 0xCF, 0x9B, 0xAB, 0x68, 0x9E]
_PARAM_STREAM_DATA_BYTES = [0xE5, 0x1D, 0x31, 0x6D, 0x2E, 0xBE, 0x82, 0x4C, 0xB7, 0x6B, 0xE7, 0x56, 0xB8, 0x81, 0x45, 0x3E]

METEXON_SERVICE_UUID = _uuid_from_le_bytes(_SERVICE_BYTES)
# RGB is handled via the SystemState structure; we keep the raw bytes defined for
# reference but do not expose a separate characteristic UUID in the codebase.

# NVS configuration service / characteristics
NVS_SERVICE_UUID = _uuid_from_le_bytes(_NVS_SERVICE_BYTES)
NVS_LIST_UUID    = _uuid_from_le_bytes(_NVS_LIST_BYTES)
NVS_GET_UUID     = _uuid_from_le_bytes(_NVS_GET_BYTES)
NVS_SET_UUID     = _uuid_from_le_bytes(_NVS_SET_BYTES)
PARAM_STREAM_SERVICE_UUID = _uuid_from_le_bytes(_PARAM_STREAM_SERVICE_BYTES)
PARAM_STREAM_LIST_UUID = _uuid_from_le_bytes(_PARAM_STREAM_LIST_BYTES)
PARAM_STREAM_CONTROL_UUID = _uuid_from_le_bytes(_PARAM_STREAM_CONTROL_BYTES)
PARAM_STREAM_DATA_UUID = _uuid_from_le_bytes(_PARAM_STREAM_DATA_BYTES)

# Canonical UUID strings for remaining characteristics (authoritative forms)
DEVICE_TYPE_UUID = UUID("68F7B778-6BFA-C2BC-4FDF-97B2CA5CAFA0")
SYSTEM_STATE_UUID = UUID("2FB1F624-DBF0-0DAD-4FAC-FE0F89988768")
MANUAL_CONTROL_UUID = UUID("56B3429F-31C5-77A7-494D-AA115E42C17B")
BLOWER_PID_UUID = UUID("60C01395-8F41-1B8F-41A4-BB012361384C")
OTA_UUID = UUID("2CD1855F-04D2-B891-4319-EDEAB7882D3E")
WIFI_UUID = UUID("07776CB4-F559-6D9C-457F-F6F0965DDABD")

ALL_UUIDS = {
    "service": METEXON_SERVICE_UUID,
    "device_type": DEVICE_TYPE_UUID,
    "system_state": SYSTEM_STATE_UUID,
    # rgb_led removed: RGB is part of the system_state characteristic
    "blower_pid": BLOWER_PID_UUID,
    "wifi": WIFI_UUID,
    "ota": OTA_UUID,
    "manual_control": MANUAL_CONTROL_UUID,
    # NVS configuration service
    "nvs_service": NVS_SERVICE_UUID,
    "nvs_list": NVS_LIST_UUID,
    "nvs_get": NVS_GET_UUID,
    "nvs_set": NVS_SET_UUID,
    "param_stream_service": PARAM_STREAM_SERVICE_UUID,
    "param_stream_list": PARAM_STREAM_LIST_UUID,
    "param_stream_control": PARAM_STREAM_CONTROL_UUID,
    "param_stream_data": PARAM_STREAM_DATA_UUID,
}

__all__ = [
    "METEXON_SERVICE_UUID",
    "DEVICE_TYPE_UUID",
    "SYSTEM_STATE_UUID",
    "BLOWER_PID_UUID",
    "WIFI_UUID",
    "OTA_UUID",
    "MANUAL_CONTROL_UUID",
    "NVS_SERVICE_UUID",
    "NVS_LIST_UUID",
    "NVS_GET_UUID",
    "NVS_SET_UUID",
    "PARAM_STREAM_SERVICE_UUID",
    "PARAM_STREAM_LIST_UUID",
    "PARAM_STREAM_CONTROL_UUID",
    "PARAM_STREAM_DATA_UUID",
    "ALL_UUIDS",
]
