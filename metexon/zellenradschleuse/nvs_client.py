"""NVS configuration access over BLE for Zellenradschleuse devices.

This module provides :class:`NVSClient`, a mixin that can be used with
:class:`~metexon.zellenradschleuse.client.ZellenradschleuseClient` to read,
write and enumerate NVS entries via the dedicated NVS BLE service.

BLE Protocol
------------
Three characteristics on the NVS service (``nvsServiceUUID``):

* **NVS List** (``NVS_LIST_UUID``):

  - Write ``{"o": <int>}`` to select the page start offset.
  - Read to receive paginated entries::

        {"entries":[{"key":..,"type":..,"desc":..,"value":..},...],
         "total":<N>, "offset":<off>, "more":<bool>}

* **NVS Get** (``NVS_GET_UUID``):

  - Write ``{"key": "<nvs_key>"}`` to select a key.
  - Read to receive the entry or ``{"error":"not_found"}``.

* **NVS Set** (``NVS_SET_UUID``):

  - Write ``{"key":"<nvs_key>","value":"<string>"}`` to set a value.
  - Read to receive ``{"status":"ok"}`` or ``{"status":"error","msg":..}``.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .constants import NVS_LIST_UUID, NVS_GET_UUID, NVS_SET_UUID


class NVSClient:
    """Mixin providing NVS read/write/list operations over BLE.

    Expects ``self._run`` and ``self.client`` (a Bleak ``BleakClient``) to
    be available, as provided by :class:`~metexon.base.BaseMetexonDevice`.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def nvs_list(self, *, include_values: bool = True) -> List[Dict[str, Any]]:
        """Return all NVS entries from the device.

        Pages through the NVS List characteristic automatically until
        ``"more"`` is ``False``.

        Parameters
        ----------
        include_values:
            When *True* (default) each dict contains a ``"value"`` key with
            the current NVS value.  Pass *False* to omit values (only
            ``"key"``, ``"type"`` and ``"desc"`` are returned) which is
            faster for pure introspection.

        Returns
        -------
        list of dict
            Each dict has keys: ``key``, ``type``, ``desc``, and (when
            *include_values* is True) ``value``.
        """
        all_entries: List[Dict[str, Any]] = []
        offset = 0
        while True:
            # Write the requested offset
            cmd = json.dumps({"o": offset}).encode()
            self._run(self.client.write_gatt_char(NVS_LIST_UUID, cmd, response=True))
            # Read paginated response
            raw = self._run(self.client.read_gatt_char(NVS_LIST_UUID))
            page = json.loads(raw.decode())
            for entry in page.get("entries", []):
                if not include_values:
                    entry.pop("value", None)
                all_entries.append(entry)
            if not page.get("more", False):
                break
            offset += len(page.get("entries", [1]))  # advance by page size
        return all_entries

    def nvs_get(self, key: str) -> Dict[str, Any]:
        """Read a single NVS entry by key.

        Parameters
        ----------
        key:
            The NVS key (as defined in firmware ``MetexonNVS.cpp``).

        Returns
        -------
        dict
            Keys: ``key``, ``type``, ``desc``, ``value``.

        Raises
        ------
        KeyError
            If the device reports the key was not found.
        """
        cmd = json.dumps({"key": key}).encode()
        self._run(self.client.write_gatt_char(NVS_GET_UUID, cmd, response=True))
        raw = self._run(self.client.read_gatt_char(NVS_GET_UUID))
        result = json.loads(raw.decode())
        if "error" in result:
            raise KeyError(f"NVS key not found: {key!r} ({result['error']})")
        return result

    def nvs_set(self, key: str, value: Any) -> None:
        """Write a single NVS value by key.

        The *value* is converted to a string before transmission (matching the
        firmware's ``setFromString`` convention).  Numeric and boolean Python
        types are handled automatically; pass a ``str`` for string NVS values.

        Parameters
        ----------
        key:
            The NVS key.
        value:
            The new value.  Will be converted to string via ``str(value)``.

        Raises
        ------
        RuntimeError
            If the device reports an error during the write.
        """
        value_str = str(value)
        cmd = json.dumps({"key": key, "value": value_str}).encode()
        self._run(self.client.write_gatt_char(NVS_SET_UUID, cmd, response=True))
        raw = self._run(self.client.read_gatt_char(NVS_SET_UUID))
        result = json.loads(raw.decode())
        if result.get("status") != "ok":
            msg = result.get("msg", "unknown error")
            raise RuntimeError(f"NVS set failed for key {key!r}: {msg}")

    def nvs_read_all(self) -> Dict[str, Any]:
        """Return all NVS values as a plain ``{key: value}`` dict.

        Convenience wrapper around :meth:`nvs_list` that returns only the
        current values keyed by their NVS key name.
        """
        entries = self.nvs_list(include_values=True)
        return {e["key"]: _coerce(e) for e in entries}

    def nvs_write_all(self, params: Dict[str, Any]) -> List[str]:
        """Write multiple NVS values from a dict.

        Parameters
        ----------
        params:
            Mapping of ``{nvs_key: value}`` to write.  Unknown keys are
            silently skipped and returned in the list of errors.

        Returns
        -------
        list of str
            Error messages for any keys that failed to write (empty on full
            success).
        """
        errors: List[str] = []
        for key, val in params.items():
            try:
                self.nvs_set(key, val)
            except (RuntimeError, KeyError) as exc:
                errors.append(str(exc))
        return errors


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _coerce(entry: Dict[str, Any]) -> Any:
    """Convert the string ``"value"`` field to its native Python type."""
    raw = entry.get("value", "")
    type_name = entry.get("type", "string")
    try:
        if type_name == "float":
            return float(raw)
        if type_name in ("uint16", "uint32", "uint64"):
            return int(raw, 0) if raw.startswith("0x") else int(raw)
    except (ValueError, TypeError):
        pass
    return raw


__all__ = ["NVSClient", "_coerce"]
