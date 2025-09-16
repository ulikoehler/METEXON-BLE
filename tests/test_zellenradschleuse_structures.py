import math
from metexon.zellenradschleuse.structures import BlowerPID, _BLOWER_PID_STRUCT

def test_zellenradschleuse_blower_pid_size():
    # Firmware sends 72 bytes (7 floats + 4x uint16 + 3x uint32 + 6 floats)
    assert _BLOWER_PID_STRUCT.size == 72


def test_zellenradschleuse_blower_pid_roundtrip():
    pid = BlowerPID(
        kp=1.0, ki=0.5, kd=0.1,
        target_frequency=100.0,
        current_frequency=95.0,
        last_error=5.0,
        integral_sum=10.0,
        current_pwm=111,
        manual_pwm_value=222,
        min_pwm_output=10,
        max_pwm_output=1023,
        update_interval_ms=50,
        flags=3,
        last_update_tick=123456,
        feed_forward=0.0,
        derivative_filter_hz=25.0,
        reserved_floats=(math.nan, math.nan, math.nan, math.nan),
    )
    data = pid.to_bytes()
    assert len(data) == _BLOWER_PID_STRUCT.size
    pid2 = BlowerPID.from_bytes(data)
    # Field-by-field comparison (handle NaNs in reserved_floats)
    assert math.isclose(pid2.kp, pid.kp, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.ki, pid.ki, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.kd, pid.kd, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.target_frequency, pid.target_frequency, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.current_frequency, pid.current_frequency, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.last_error, pid.last_error, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.integral_sum, pid.integral_sum, rel_tol=1e-6, abs_tol=0.0)
    assert pid2.current_pwm == pid.current_pwm
    assert pid2.manual_pwm_value == pid.manual_pwm_value
    assert pid2.min_pwm_output == pid.min_pwm_output
    assert pid2.max_pwm_output == pid.max_pwm_output
    assert pid2.update_interval_ms == pid.update_interval_ms
    assert pid2.flags == pid.flags
    assert pid2.last_update_tick == pid.last_update_tick
    assert math.isclose(pid2.feed_forward, pid.feed_forward, rel_tol=1e-6, abs_tol=0.0)
    assert math.isclose(pid2.derivative_filter_hz, pid.derivative_filter_hz, rel_tol=1e-6, abs_tol=0.0)
    for a, b in zip(pid2.reserved_floats, pid.reserved_floats):
        if math.isnan(b):
            assert math.isnan(a)
        else:
            assert a == b
