from piservo0 import PiServo

def test_init(mocker):
    """
    __init__()
    """
    mock_pi = mocker.Mock()
    servo = PiServo(mock_pi, 18, debug=True)
    assert servo.pi is mock_pi
    assert not hasattr(servo, 'mypi')

def test_move(mocker):
    """
    move()
    """
    mock_pi = mocker.Mock()
    servo = PiServo(mock_pi, 18, debug=True)

    # move to center
    servo.move(PiServo.CENTER)
    servo.pi.set_servo_pulsewidth.assert_called_with(18, 1500)

    # move to min
    servo.move(PiServo.MIN)
    servo.pi.set_servo_pulsewidth.assert_called_with(18, 500)

    # move to max
    servo.move(PiServo.MAX)
    servo.pi.set_servo_pulsewidth.assert_called_with(18, 2500)

def test_move_limit(mocker):
    """
    move() limit
    """
    mock_pi = mocker.Mock()
    servo = PiServo(mock_pi, 18, debug=True)

    # move under min
    servo.move(PiServo.MIN - 100)
    servo.pi.set_servo_pulsewidth.assert_called_with(18, PiServo.MIN)

    # move over max
    servo.move(PiServo.MAX + 100)
    servo.pi.set_servo_pulsewidth.assert_called_with(18, PiServo.MAX)

def test_off(mocker):
    """
    off()
    """
    mock_pi = mocker.Mock()
    servo = PiServo(mock_pi, 18, debug=True)
    servo.off()
    servo.pi.set_servo_pulsewidth.assert_called_with(18, PiServo.OFF)