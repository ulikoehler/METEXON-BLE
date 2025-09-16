from metexon.structures import SystemState, ManualControl, BlowerPID, RGB
import math


def test_system_state_roundtrip():
    ss = SystemState(
        state=3,
        pressure1=1.1,
        pressure2=2.2,
        absPressure=3.3,
        motorCurrent=4.4,
        getriebemotorPWM=123,
        vibrationsmotorPWM=456,
        blowerPWM=789,
        blowerPulseRateRPM=1500.5,
        rgb=[RGB(10,20,30), RGB(40,50,60)],
        encoderCount=42,
        blowerPulseCount=9999,
    )
    data = ss.to_bytes()
    ss2 = SystemState.from_bytes(data)
    assert ss2.to_json() == ss.to_json()


def test_manual_control_roundtrip():
    mc = ManualControl(
        blower_rpm=1200.0,
        getriebemotor_pwm=55.5,
        vibrationsmotor_pwm=66.6,
        enable_getriebemotor_nvs=1,
        feeder_seconds=5.0,
    )
    data = mc.to_bytes()
    mc2 = ManualControl.from_bytes(data)
    assert mc2.to_json() == mc.to_json()


def test_blower_pid_roundtrip():
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
    pid2 = BlowerPID.from_bytes(data)
    j1 = pid.to_json(); j2 = pid2.to_json()
    # NaNs won't compare equal; check individually
    for k, v in j1.items():
        if isinstance(v, float) and math.isnan(v):
            assert math.isnan(j2[k])
        else:
            assert j2[k] == v
