#
# (c) 2025 Yoichi Tanibayashi
#
import pytest
import pigpio
from unittest.mock import patch
from piservo0.cmd_multi import CmdMulti


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


@pytest.fixture
def multi_app():
    """CmdMultiのテスト用インスタンス"""
    app = CmdMulti([17, 27, 22, 23], './servo_test.json', debug=True)
    yield app
    app.end()


def test_cmd_multi_init_ok(multi_app):
    """CmdMulti.__init__()"""
    assert multi_app.pin == [17, 27, 22, 23]
    assert multi_app.conf_file == './servo_test.json'
    assert multi_app.pi.connected


def test_cmd_multi_main(multi_app, mocker, capsys):
    """CmdMulti.main()"""
    mocker.patch('builtins.input', side_effect=['10.5 -20.0 30.0 -40.0', 'invalid', 'q'])

    mock_ctx = mocker.MagicMock()
    mock_ctx.command.name = 'multi'
    mocker.patch.object(multi_app._log, 'error')
    multi_app.main(mock_ctx)

    moved_angles = multi_app.servo.get_angle()
    assert pytest.approx(moved_angles[0], abs=1.0) == 10.5
    assert pytest.approx(moved_angles[1], abs=1.0) == -20.0

    multi_app._log.error.assert_called_once()


def test_cmd_multi_main_eof(multi_app, mocker):
    """CmdMulti.main() EOFError"""
    mocker.patch('builtins.input', side_effect=EOFError)
    mock_ctx = mocker.MagicMock()
    mock_ctx.command.name = 'multi'
    multi_app.main(mock_ctx)
    # 例外が発生しても、正常に終了することを確認
    # app.end()が呼ばれるので、pi.stop()も呼ばれるはず