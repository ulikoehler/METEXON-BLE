"""Characteristic UUIDs for Zellenradschleuse devices.

Imports base UUID constants from metexon.constants but re-exports them under
namespaced module for clarity.
"""
from __future__ import annotations

from ..constants import (
    METEXON_SERVICE_UUID,
    DEVICE_TYPE_UUID,
    SYSTEM_STATE_UUID,
    BLOWER_PID_UUID,
    WIFI_UUID,
    OTA_UUID,
    MANUAL_CONTROL_UUID,
    NVS_SERVICE_UUID,
    NVS_LIST_UUID,
    NVS_GET_UUID,
    NVS_SET_UUID,
    PARAM_STREAM_SERVICE_UUID,
    PARAM_STREAM_LIST_UUID,
    PARAM_STREAM_CONTROL_UUID,
    PARAM_STREAM_DATA_UUID,
)

__all__ = [
    'METEXON_SERVICE_UUID',
    'DEVICE_TYPE_UUID',
    'SYSTEM_STATE_UUID',
    'BLOWER_PID_UUID',
    'WIFI_UUID',
    'OTA_UUID',
    'MANUAL_CONTROL_UUID',
    'NVS_SERVICE_UUID',
    'NVS_LIST_UUID',
    'NVS_GET_UUID',
    'NVS_SET_UUID',
    'PARAM_STREAM_SERVICE_UUID',
    'PARAM_STREAM_LIST_UUID',
    'PARAM_STREAM_CONTROL_UUID',
    'PARAM_STREAM_DATA_UUID',
]
