import time
import random
import pigpio
from piservo0 import MultiServo

PIN = [18, 21, 24]  # !! Ajust your configuration

try:
    pi = pigpio.pi()

    servo = MultiServo(pi, PIN)
    time.sleep(2)

    count = 0
    while True:
        for s in (2.0, 1.0, 0.5, 0.3):
            for i in range(5):
                count += 1

                angle = [
                    round(random.uniform(-90, 90)),
                    round(random.uniform(-90, 90)),
                    round(random.uniform(-90, 90))
                ]

                print(f'{count:>3}: {s} sec: {angle}')
                servo.move_angle_sync(angle, s)

            print()
            time.sleep(1)

except KeyboardInterrupt as e:
    print(f'\n !! {type(e)}: {e}')

except Exception as e:
    print(f'\n !! {type(e)}: {e}')

finally:
    time.sleep(1)
    servo.move_angle([0] * len(PIN))
    time.sleep(1)
    servo.off()
    pi.stop()
    print('\n END\n')
