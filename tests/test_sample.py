import unittest
from unittest.mock import MagicMock, patch
import time
import pigpio
from piservo0 import PiServo

class TestSample(unittest.TestCase):

    @patch('pigpio.pi')
    @patch('piservo0.piservo.PiServo')
    def test_sample_script(self, MockPiServo, MockPigpioPi):
        # pigpio.pi() のモックを設定
        mock_pi_instance = MockPigpioPi.return_value
        mock_pi_instance.connected = True

        # PiServo のモックを設定
        mock_servo_instance = MockPiServo.return_value

        # time.sleep をモックして実際の待機をなくす
        with patch('time.sleep', return_value=None):
            # samples/sample.py の内容を模倣
            # pi = pigpio.pi()
            # if not pi.connected:
            #     exit()
            # servo = PiServo(pi, 18, debug=True)
            # try:
            #     servo.move(PiServo.CENTER)
            #     time.sleep(1)
            #     servo.move(PiServo.MIN)
            #     time.sleep(1)
            #     servo.move(PiServo.MAX)
            #     time.sleep(1)
            #     servo.move(PiServo.CENTER)
            #     time.sleep(1)
            # finally:
            #     servo.off()
            #     pi.stop()

            # ここからが実際のテスト対象のロジック
            pi = MockPigpioPi()
            self.assertTrue(pi.connected) # 接続されていることを確認

            servo = MockPiServo(pi, 18, debug=True)

            servo.move(PiServo.CENTER)
            time.sleep(1)
            servo.move(PiServo.MIN)
            time.sleep(1)
            servo.move(PiServo.MAX)
            time.sleep(1)
            servo.move(PiServo.CENTER)
            time.sleep(1)

            servo.off()
            pi.stop()

            # 各メソッドが期待通りに呼び出されたか検証
            MockPigpioPi.assert_called_once()
            mock_pi_instance.stop.assert_called_once()
            MockPiServo.assert_called_once_with(mock_pi_instance, 18, debug=True)
            mock_servo_instance.move.assert_any_call(PiServo.CENTER)
            mock_servo_instance.move.assert_any_call(PiServo.MIN)
            mock_servo_instance.move.assert_any_call(PiServo.MAX)
            self.assertEqual(mock_servo_instance.move.call_count, 4)
            mock_servo_instance.off.assert_called_once()

if __name__ == '__main__':
    unittest.main()
