import time
import pigpio
from piservo0 import CalibrableServo

PIN1 = 17
PIN2 = 22

TOTAL_ANGLE1 = 180.0
TOTAL_ANGLE2 = 90.0

LOOP_N = 10
SLEEP_SEC = 0.06


pi = pigpio.pi()

servo1 = CalibrableServo(pi, PIN1)
servo2 = CalibrableServo(pi, PIN2)

angle1 = angle2 = CalibrableServo.ANGLE_MIN
servo1.move_angle(angle1)
servo2.move_angle(angle2)
time.sleep(2)

time_start = time.time()
print(f'{time.time() - time_start:.3f}: --- START ---')

for i in range(LOOP_N):
    angle1 += TOTAL_ANGLE1 / LOOP_N
    angle2 += TOTAL_ANGLE2 / LOOP_N

    servo1.move_angle(angle1)
    servo2.move_angle(angle2)

    time.sleep(SLEEP_SEC)

    print(f'{time.time() - time_start:.3f}: {angle1: >6},{angle2: >6}')

servo1.off()
servo2.off()
pi.stop()
