import time
import pigpio
from piservo0 import MultiServo

PIN = [18, 21, 24]  # !! Ajust your configuration

try:
    pi = pigpio.pi()

    servo = MultiServo(pi, PIN)
    time.sleep(2)


    ###
    print('* move_angle_sync()\n')

    for sec in [2, 1, 0.5, 0.3]:
        print(f' sec={sec}')

        servo.move_angle([-90,-90,-90])
        time.sleep(2)

        for angles in [
                        [ 90,  0,-45],
                        [-90, 90,  0],
                        [ 90,  0, 45],
                        [-90,-90, 90]
                      ]:
            print(f' angles={angles}')
            servo.move_angle_sync(angles, sec)

        time.sleep(2)

        print()

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
    print('* END\n')
