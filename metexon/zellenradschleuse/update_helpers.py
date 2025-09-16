"""Helper functions to create partial update dataclasses using sentinel values."""
from __future__ import annotations

from .structures import SystemState, ManualControl, BlowerPID
from . import sentinels as S

__all__ = [
    'partial_system_state', 'partial_manual_control', 'partial_blower_pid'
]

def partial_system_state(**kwargs) -> SystemState:
    """Create a SystemState object with only provided fields changed.

    Fields not specified are filled with the appropriate sentinel (NaN or no-change integers).
    Accepts rgb as list of 2 (r,g,b) tuples.
    """
    rgb = kwargs.pop('rgb', [(0,0,0), (0,0,0)])
    # Provide defaults with sentinel semantics
    return SystemState.from_json({
        'state': kwargs.get('state', 0),  # state typically read-only
        'pressure1': kwargs.get('pressure1', S.FLOAT_NO_CHANGE),
        'pressure2': kwargs.get('pressure2', S.FLOAT_NO_CHANGE),
        'absPressure': kwargs.get('absPressure', S.FLOAT_NO_CHANGE),
        'motorCurrent': kwargs.get('motorCurrent', S.FLOAT_NO_CHANGE),
        'getriebemotorPWM': kwargs.get('getriebemotorPWM', S.PWM_NO_CHANGE),
        'vibrationsmotorPWM': kwargs.get('vibrationsmotorPWM', S.PWM_NO_CHANGE),
        'blowerPWM': kwargs.get('blowerPWM', S.PWM_NO_CHANGE),
        'blowerPulseRateRPM': kwargs.get('blowerPulseRateRPM', S.FLOAT_NO_CHANGE),
        'rgb': rgb,
        'encoderCount': kwargs.get('encoderCount', S.ENCODER_NO_CHANGE),
        'blowerPulseCount': kwargs.get('blowerPulseCount', S.U32_NO_CHANGE),
    })

def partial_manual_control(**kwargs) -> ManualControl:
    return ManualControl.from_json({
        'blower_rpm': kwargs.get('blower_rpm', S.FLOAT_NO_CHANGE),
        'getriebemotor_pwm': kwargs.get('getriebemotor_pwm', S.FLOAT_NO_CHANGE),
        'vibrationsmotor_pwm': kwargs.get('vibrationsmotor_pwm', S.FLOAT_NO_CHANGE),
        'enable_getriebemotor_nvs': kwargs.get('enable_getriebemotor_nvs', 0),
        'feeder_seconds': kwargs.get('feeder_seconds', S.FLOAT_NO_CHANGE),
        'reserved': kwargs.get('reserved', [0]*8),
    })

def partial_blower_pid(**kwargs) -> BlowerPID:
    return BlowerPID.from_json({
        'kp': kwargs.get('kp', S.FLOAT_NO_CHANGE),
        'ki': kwargs.get('ki', S.FLOAT_NO_CHANGE),
        'kd': kwargs.get('kd', S.FLOAT_NO_CHANGE),
        'target_frequency': kwargs.get('target_frequency', S.FLOAT_NO_CHANGE),
        'current_frequency': kwargs.get('current_frequency', S.FLOAT_NO_CHANGE),
        'last_error': kwargs.get('last_error', S.FLOAT_NO_CHANGE),
        'integral_sum': kwargs.get('integral_sum', S.FLOAT_NO_CHANGE),
        'current_pwm': kwargs.get('current_pwm', S.PWM_NO_CHANGE),
        'manual_pwm_value': kwargs.get('manual_pwm_value', S.PWM_NO_CHANGE),
        'min_pwm_output': kwargs.get('min_pwm_output', S.PWM_NO_CHANGE),
        'max_pwm_output': kwargs.get('max_pwm_output', S.PWM_NO_CHANGE),
        'update_interval_ms': kwargs.get('update_interval_ms', 0),
        'flags': kwargs.get('flags', 0),
        'last_update_tick': kwargs.get('last_update_tick', 0),
        'feed_forward': kwargs.get('feed_forward', S.FLOAT_NO_CHANGE),
        'derivative_filter_hz': kwargs.get('derivative_filter_hz', S.FLOAT_NO_CHANGE),
        'reserved_floats': kwargs.get('reserved_floats', [S.FLOAT_NO_CHANGE]*4),
    })
