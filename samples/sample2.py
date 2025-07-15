import time
import pigpio
from piservo0 import CalibrableServo

PIN1 = 18
PIN2 = 21

TOTAL_ANGLE1 = 180
TOTAL_ANGLE2 = 90

LOOP_N = 10
SLEEP_SEC = 0.06


pi = pigpio.pi()

servo1 = CalibrableServo(pi, PIN1)
servo2 = CalibrableServo(pi, PIN2)

angle1 = angle2 = CalibrableServo.ANGLE_MIN
servo1.move_angle(angle1)
servo2.move_angle(angle2)
time.sleep(1)

for i in range(LOOP_N + 1):
    print(f'{angle1}, {angle2}')

    servo1.move_angle(angle1)
    servo2.move_angle(angle2)

    angle1 += TOTAL_ANGLE1 / LOOP_N
    angle2 += TOTAL_ANGLE2 / LOOP_N

    time.sleep(SLEEP_SEC)

servo1.off()
servo2.off()
pi.stop()
