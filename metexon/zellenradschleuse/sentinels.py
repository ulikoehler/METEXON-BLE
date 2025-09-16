"""Sentinel constants for partial updates to Zellenradschleuse characteristics.

These values mirror firmware semantics:
- Floats: use NaN to mean "leave unchanged"
- Unsigned 16-bit PWM fields: 0xFFFF
- Signed 32-bit encoder counter: INT32_MIN (-2147483648)
- Unsigned 32-bit counters: 0xFFFFFFFF
- RGB components: 0xFF may be interpreted as no-change (if firmware supports)

Providing named constants avoids users needing to memorize numeric values.
"""
from __future__ import annotations

import math

FLOAT_NO_CHANGE = math.nan
PWM_NO_CHANGE = 0xFFFF
ENCODER_NO_CHANGE = -2**31  # INT32_MIN
U32_NO_CHANGE = 0xFFFFFFFF
RGB_NO_CHANGE_COMPONENT = 0xFF

__all__ = [
    "FLOAT_NO_CHANGE",
    "PWM_NO_CHANGE",
    "ENCODER_NO_CHANGE",
    "U32_NO_CHANGE",
    "RGB_NO_CHANGE_COMPONENT",
]
