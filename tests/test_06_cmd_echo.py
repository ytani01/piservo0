#
# (c) 2025 Yoichi Tanibayashi
#
from piservo0.cmd_echo import CmdEcho


def test_cmd_echo_main(capsys, mocker):
    """
    CmdEcho.main()
    """
    mocker.patch('time.sleep', return_value=None)

    app = CmdEcho(debug=True)
    app.main()
    captured = capsys.readouterr()
    assert captured.out == 'this is sample command \n'


def test_cmd_echo_end(capsys):
    """
    CmdEcho.end()
    """
    app = CmdEcho(debug=True)
    app.end()
    captured = capsys.readouterr()
    assert captured.out == 'bye!\n'
