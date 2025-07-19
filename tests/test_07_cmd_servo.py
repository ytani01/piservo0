#
# (c) 2025 Yoichi Tanibayashi
#
import pytest
import pigpio
from piservo0.cmd_servo import CmdServo
from piservo0.piservo import PiServo

PIN = 17

def check_pigpiod():
    """Check if pigpiod is running"""
    try:
        pi = pigpio.pi()
        if not pi.connected:
            return False
        pi.stop()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not check_pigpiod(), reason="pigpiod is not running")


def test_cmd_servo_init_ok():
    """CmdServo.__init__()"""
    pi = pigpio.pi()
    app = CmdServo(pi, PIN, "1500", 1.2, debug=True)
    assert app.pin == PIN
    assert app.pulse_str == "1500"
    assert app.sec == 1.2
    assert app.pi.connected
    app.end()
    pi.stop()


def test_cmd_servo_main():
    """CmdServo.main()"""
    pi = pigpio.pi()
    # 数値
    app = CmdServo(pi, PIN, "1500", 1.0, debug=True)
    app.main()
    # 例外が出なければOK

    # 文字列
    app = CmdServo(pi, PIN, "min", 1.0, debug=True)
    app.main()

    app = CmdServo(pi, PIN, "max", 1.0, debug=True)
    app.main()

    app = CmdServo(pi, PIN, "center", 1.0, debug=True)
    app.main()

    # 不正な文字列
    app = CmdServo(pi, PIN, "invalid", 1.0, debug=True)
    app.main()

    # 不正な値
    app = CmdServo(pi, PIN, str(PiServo.MIN - 1), 1.0, debug=True)
    app.main()

    app.end()
    pi.stop()


def test_cmd_servo_end(capsys):
    """CmdServo.end()"""
    pi = pigpio.pi()
    app = CmdServo(pi, PIN, "1500", 1.0, debug=True)
    app.end()
    captured = capsys.readouterr()
    assert captured.out == 'bye!\n'
    pi.stop()
