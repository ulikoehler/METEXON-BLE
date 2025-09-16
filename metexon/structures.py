"""Binary structure (de)serialization helpers for Metexon BLE characteristics.

The struct layouts are mirrored from the firmware C++ definitions. We use
`struct` module with little-endian packing. All floats are IEEE-754
single-precision.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple
import math
import struct

# ================= SystemStateBinary ==================
# C struct layout (packed):
# uint8_t state;
# float pressure1;
# float pressure2;
# float absPressure;
# float motorCurrent;
# uint16_t getriebemotorPWM;
# uint16_t vibrationsmotorPWM;
# uint16_t blowerPWM;
# float blowerPulseRateRPM;
# struct RGB { uint8_t r,g,b; } rgb[2];  // 6 bytes
# int32_t encoderCount;
# uint32_t blowerPulseCount;
# Total size check for safety

_SYSTEM_STATE_STRUCT = struct.Struct('<BffffHHHfBBBBBBiI')
# Explanation of format:
# < little-endian
# B state
# f pressure1
# f pressure2
# f absPressure
# f motorCurrent
# H getriebemotorPWM
# H vibrationsmotorPWM
# H blowerPWM
# f blowerPulseRateRPM
# B rgb0.r
# B rgb0.g
# B rgb0.b
# B rgb1.r
# B rgb1.g
# B rgb1.b
# i encoderCount
# I blowerPulseCount

@dataclass
class RGB:
    red: int
    green: int
    blue: int

    def to_tuple(self) -> Tuple[int, int, int]:
        return self.red, self.green, self.blue

    @classmethod
    def from_tuple(cls, t: Tuple[int, int, int]) -> 'RGB':
        return cls(*t)

@dataclass
class SystemState:
    state: int
    pressure1: float
    pressure2: float
    absPressure: float
    motorCurrent: float
    getriebemotorPWM: int
    vibrationsmotorPWM: int
    blowerPWM: int
    blowerPulseRateRPM: float
    rgb: List[RGB]
    encoderCount: int
    blowerPulseCount: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'SystemState':
        if len(data) != _SYSTEM_STATE_STRUCT.size:
            raise ValueError(f"SystemStateBinary expected {_SYSTEM_STATE_STRUCT.size} bytes, got {len(data)}")
        unpacked = _SYSTEM_STATE_STRUCT.unpack(data)
        (
            state,
            pressure1,
            pressure2,
            absPressure,
            motorCurrent,
            getriebemotorPWM,
            vibrationsmotorPWM,
            blowerPWM,
            blowerPulseRateRPM,
            r0, g0, b0, r1, g1, b1,
            encoderCount,
            blowerPulseCount,
        ) = unpacked
        return cls(
            state=state,
            pressure1=pressure1,
            pressure2=pressure2,
            absPressure=absPressure,
            motorCurrent=motorCurrent,
            getriebemotorPWM=getriebemotorPWM,
            vibrationsmotorPWM=vibrationsmotorPWM,
            blowerPWM=blowerPWM,
            blowerPulseRateRPM=blowerPulseRateRPM,
            rgb=[RGB(r0, g0, b0), RGB(r1, g1, b1)],
            encoderCount=encoderCount,
            blowerPulseCount=blowerPulseCount,
        )

    def to_bytes(self) -> bytes:
        (r0, g0, b0) = self.rgb[0].to_tuple() if self.rgb else (0, 0, 0)
        (r1, g1, b1) = self.rgb[1].to_tuple() if len(self.rgb) > 1 else (0, 0, 0)
        return _SYSTEM_STATE_STRUCT.pack(
            self.state,
            self.pressure1,
            self.pressure2,
            self.absPressure,
            self.motorCurrent,
            self.getriebemotorPWM,
            self.vibrationsmotorPWM,
            self.blowerPWM,
            self.blowerPulseRateRPM,
            r0, g0, b0, r1, g1, b1,
            self.encoderCount,
            self.blowerPulseCount,
        )

    def to_json(self) -> Dict[str, Any]:
        # Quantize floats to IEEE-754 single-precision so JSON representation
        # matches the packed/unpacked values used by to_bytes()/from_bytes().
        def f32(v: float) -> float:
            return struct.unpack('<f', struct.pack('<f', float(v)))[0]

        d = asdict(self)
        d['rgb'] = [c.to_tuple() for c in self.rgb]
        d['pressure1'] = f32(d['pressure1'])
        d['pressure2'] = f32(d['pressure2'])
        d['absPressure'] = f32(d['absPressure'])
        d['motorCurrent'] = f32(d['motorCurrent'])
        d['blowerPulseRateRPM'] = f32(d['blowerPulseRateRPM'])
        return d

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> 'SystemState':
        rgb_list = d.get('rgb', [(0,0,0), (0,0,0)])
        rgb_objs = [RGB.from_tuple(tuple(t)) for t in rgb_list]
        return cls(
            state=d.get('state', 0),
            pressure1=d.get('pressure1', math.nan),
            pressure2=d.get('pressure2', math.nan),
            absPressure=d.get('absPressure', math.nan),
            motorCurrent=d.get('motorCurrent', math.nan),
            getriebemotorPWM=d.get('getriebemotorPWM', 0xFFFF),
            vibrationsmotorPWM=d.get('vibrationsmotorPWM', 0xFFFF),
            blowerPWM=d.get('blowerPWM', 0xFFFF),
            blowerPulseRateRPM=d.get('blowerPulseRateRPM', math.nan),
            rgb=rgb_objs,
            encoderCount=d.get('encoderCount', -2**31),
            blowerPulseCount=d.get('blowerPulseCount', 0xFFFFFFFF),
        )

# =============== ManualControlBinary ==================
# struct ManualControlBinary {
#   float blower_rpm;
#   float getriebemotor_pwm;
#   float vibrationsmotor_pwm;
#   uint8_t enable_getriebemotor_nvs;
#   float feeder_seconds;
#   uint8_t reserved[8];
# } // <= 32 bytes
_MANUAL_CONTROL_STRUCT = struct.Struct('<fffBf8s')

@dataclass
class ManualControl:
    blower_rpm: float
    getriebemotor_pwm: float
    vibrationsmotor_pwm: float
    enable_getriebemotor_nvs: int
    feeder_seconds: float
    reserved: bytes = b'\x00' * 8

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ManualControl':
        if len(data) != _MANUAL_CONTROL_STRUCT.size:
            raise ValueError(f"ManualControlBinary expected {_MANUAL_CONTROL_STRUCT.size} bytes, got {len(data)}")
        blower_rpm, getriebemotor_pwm, vibrationsmotor_pwm, enable, feeder_seconds, reserved = _MANUAL_CONTROL_STRUCT.unpack(data)
        return cls(blower_rpm, getriebemotor_pwm, vibrationsmotor_pwm, enable, feeder_seconds, reserved)

    def to_bytes(self) -> bytes:
        return _MANUAL_CONTROL_STRUCT.pack(
            self.blower_rpm,
            self.getriebemotor_pwm,
            self.vibrationsmotor_pwm,
            self.enable_getriebemotor_nvs,
            self.feeder_seconds,
            self.reserved,
        )

    def to_json(self) -> Dict[str, Any]:
        def f32(v: float) -> float:
            return struct.unpack('<f', struct.pack('<f', float(v)))[0]

        d = asdict(self)
        d['reserved'] = list(self.reserved)
        d['blower_rpm'] = f32(d['blower_rpm'])
        d['getriebemotor_pwm'] = f32(d['getriebemotor_pwm'])
        d['vibrationsmotor_pwm'] = f32(d['vibrationsmotor_pwm'])
        d['feeder_seconds'] = f32(d['feeder_seconds'])
        return d

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> 'ManualControl':
        return cls(
            blower_rpm=d.get('blower_rpm', math.nan),
            getriebemotor_pwm=d.get('getriebemotor_pwm', math.nan),
            vibrationsmotor_pwm=d.get('vibrationsmotor_pwm', math.nan),
            enable_getriebemotor_nvs=d.get('enable_getriebemotor_nvs', 0),
            feeder_seconds=d.get('feeder_seconds', math.nan),
            reserved=bytes(d.get('reserved', [0]*8))[:8].ljust(8, b'\x00'),
        )

# =============== BlowerPIDBinary ==================
# struct BlowerPIDBinary {
#   float kp, ki, kd;
#   float target_frequency;
#   float current_frequency;
#   float last_error;
#   float integral_sum;
#   uint16_t current_pwm;
#   uint16_t manual_pwm_value;
#   uint16_t min_pwm_output;
#   uint16_t max_pwm_output;
#   uint32_t update_interval_ms;
#   uint32_t flags;
#   uint32_t last_update_tick;
#   float feed_forward;
#   float derivative_filter_hz;
#   float reserved_floats[4];
# } <= 128 bytes
_BLOWER_PID_STRUCT = struct.Struct('<fffffffHHHHIIIff4f')

@dataclass
class BlowerPID:
    kp: float
    ki: float
    kd: float
    target_frequency: float
    current_frequency: float
    last_error: float
    integral_sum: float
    current_pwm: int
    manual_pwm_value: int
    min_pwm_output: int
    max_pwm_output: int
    update_interval_ms: int
    flags: int
    last_update_tick: int
    feed_forward: float
    derivative_filter_hz: float
    reserved_floats: Tuple[float, float, float, float]

    @classmethod
    def from_bytes(cls, data: bytes) -> 'BlowerPID':
        if len(data) != _BLOWER_PID_STRUCT.size:
            raise ValueError(f"BlowerPIDBinary expected {_BLOWER_PID_STRUCT.size} bytes, got {len(data)}")
        unpacked = _BLOWER_PID_STRUCT.unpack(data)
        return cls(
            kp=unpacked[0],
            ki=unpacked[1],
            kd=unpacked[2],
            target_frequency=unpacked[3],
            current_frequency=unpacked[4],
            last_error=unpacked[5],
            integral_sum=unpacked[6],
            current_pwm=unpacked[7],
            manual_pwm_value=unpacked[8],
            min_pwm_output=unpacked[9],
            max_pwm_output=unpacked[10],
            update_interval_ms=unpacked[11],
            flags=unpacked[12],
            last_update_tick=unpacked[13],
            feed_forward=unpacked[14],
            derivative_filter_hz=unpacked[15],
            reserved_floats=unpacked[16:20],
        )

    def to_bytes(self) -> bytes:
        return _BLOWER_PID_STRUCT.pack(
            self.kp,
            self.ki,
            self.kd,
            self.target_frequency,
            self.current_frequency,
            self.last_error,
            self.integral_sum,
            self.current_pwm,
            self.manual_pwm_value,
            self.min_pwm_output,
            self.max_pwm_output,
            self.update_interval_ms,
            self.flags,
            self.last_update_tick,
            self.feed_forward,
            self.derivative_filter_hz,
            *self.reserved_floats,
        )

    def to_json(self) -> Dict[str, Any]:
        def f32(v: float) -> float:
            return struct.unpack('<f', struct.pack('<f', float(v)))[0]

        d = asdict(self)
        # Quantize all floats to 32-bit precision to match binary roundtrip
        d['kp'] = f32(d['kp'])
        d['ki'] = f32(d['ki'])
        d['kd'] = f32(d['kd'])
        d['target_frequency'] = f32(d['target_frequency'])
        d['current_frequency'] = f32(d['current_frequency'])
        d['last_error'] = f32(d['last_error'])
        d['integral_sum'] = f32(d['integral_sum'])
        d['feed_forward'] = f32(d['feed_forward'])
        d['derivative_filter_hz'] = f32(d['derivative_filter_hz'])
        # Represent NaN reserved slots as None so JSON/list equality works when
        # comparing round-tripped structures (NaN != NaN breaks direct list
        # comparisons).
        def _nan_safe(x: float):
            return None if math.isnan(x) else f32(x)

        d['reserved_floats'] = [_nan_safe(x) for x in d['reserved_floats']]
        return d

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> 'BlowerPID':
        return cls(
            kp=d.get('kp', math.nan),
            ki=d.get('ki', math.nan),
            kd=d.get('kd', math.nan),
            target_frequency=d.get('target_frequency', math.nan),
            current_frequency=d.get('current_frequency', math.nan),
            last_error=d.get('last_error', math.nan),
            integral_sum=d.get('integral_sum', math.nan),
            current_pwm=d.get('current_pwm', 0xFFFF),
            manual_pwm_value=d.get('manual_pwm_value', 0xFFFF),
            min_pwm_output=d.get('min_pwm_output', 0xFFFF),
            max_pwm_output=d.get('max_pwm_output', 0xFFFF),
            update_interval_ms=d.get('update_interval_ms', 0),
            flags=d.get('flags', 0),
            last_update_tick=d.get('last_update_tick', 0),
            feed_forward=d.get('feed_forward', math.nan),
            derivative_filter_hz=d.get('derivative_filter_hz', math.nan),
            reserved_floats=tuple(d.get('reserved_floats', [math.nan]*4))[:4],
        )

__all__ = [
    'SystemState', 'ManualControl', 'BlowerPID', 'RGB'
]
