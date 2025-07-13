import pytest
import time
import pigpio
from piservo0 import PiServo

SLEEP_SEC = 0.8
TEST_PIN = 18

def new_servo(pin):
    """
    """
    pi = pigpio.pi()

    servo = PiServo(pi, pin, debug=True)

    return (pi, servo)

def end_test(pi):
    """
    """
    pi.stop()

def test_create():
    """
    """
    pi, servo = new_servo(TEST_PIN)

    assert type(servo) is PiServo

    end_test(pi)

def test_center():
    """
    """
    pi, servo = new_servo(TEST_PIN)

    servo.center()
    time.sleep(SLEEP_SEC)

    pulse_res = servo.get()

    assert pulse_res == PiServo.CENTER

    end_test(pi)

def test_min():
    """
    """
    pi, servo = new_servo(TEST_PIN)

    servo.min()
    time.sleep(SLEEP_SEC)

    pulse_res = servo.get()

    assert pulse_res == PiServo.MIN

    end_test(pi)

def test_max():
    """
    """
    pi, servo = new_servo(TEST_PIN)

    servo.max()
    time.sleep(SLEEP_SEC)

    pulse_res = servo.get()

    assert pulse_res == PiServo.MAX

    end_test(pi)

@pytest.mark.parametrize(('pulse', "expected"), [
    (1000, 1000),
    (2000, 2000),
    (PiServo.MIN, PiServo.MIN),
    (PiServo.MAX, PiServo.MAX),
    (10, PiServo.MIN),
    (5000, PiServo.MAX),
    (PiServo.CENTER, PiServo.CENTER),
])
def test_move(pulse, expected):
    """
    """
    pi, servo = new_servo(TEST_PIN)

    servo.move(pulse)
    time.sleep(SLEEP_SEC)

    pulse_res = servo.get()

    assert pulse_res == expected

    end_test(pi)
