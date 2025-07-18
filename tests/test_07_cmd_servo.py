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
    app = CmdServo(PIN, "1500", 1.2, debug=True)
    assert app.pin == PIN
    assert app.pulse_str == "1500"
    assert app.sec == 1.2
    assert app.pi.connected
    app.end()


def test_cmd_servo_main():
    """CmdServo.main()"""
    # 数値
    app = CmdServo(PIN, "1500", debug=True)
    app.main()
    # 例外が出なければOK

    # 文字列
    app = CmdServo(PIN, "min", debug=True)
    app.main()

    app = CmdServo(PIN, "max", debug=True)
    app.main()

    app = CmdServo(PIN, "center", debug=True)
    app.main()

    # 不正な文字列
    app = CmdServo(PIN, "invalid", debug=True)
    app.main()

    # 不正な値
    app = CmdServo(PIN, str(PiServo.MIN - 1), debug=True)
    app.main()

    app.end()


def test_cmd_servo_end(capsys):
    """CmdServo.end()"""
    app = CmdServo(PIN, "1500", debug=True)
    app.end()
    captured = capsys.readouterr()
    assert captured.out == 'bye!\n'
