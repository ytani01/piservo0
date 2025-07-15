import time
import pigpio
from piservo0 import CalibrableServo

PIN1 = 18
PIN2 = 21
SLEEP_SEC = 0.025

pi = pigpio.pi()

servo1 = CalibrableServo(pi, PIN1)
servo2 = CalibrableServo(pi, PIN2)

angle1 = angle2 = -90
servo1.move_angle(angle1)
servo2.move_angle(angle2)
time.sleep(1)

for i in range(21):
    print(f'{angle1}, {angle2}')

    servo1.move_angle(angle1)
    servo2.move_angle(angle2)

    angle1 += 9
    angle2 += 4.5

    time.sleep(SLEEP_SEC)

servo1.off()
servo2.off()
pi.stop()
