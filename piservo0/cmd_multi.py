#
# (c) 2025 Yoichi Tanibayashi
#
import time
import pigpio
from .multi_servo import MultiServo
from .my_logger import get_logger


class CmdMulti:
    """ multi servo controller """
    def __init__(self, pin, conf_file, sec=1.0, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pin=%s,conf_file=%s,sec=%s', pin, conf_file, sec)

        self.pin = pin
        self.conf_file = conf_file
        self.sec = sec

        self.pi = pigpio.pi()
        if not self.pi.connected:
            self._log.error('pigpio daemon not connected.')
            raise ConnectionError('pigpio daemon not connected.')

        try:
            self.servo = MultiServo(self.pi, self.pin, self.conf_file,
                                    debug=self._dbg)
        except Exception as _e:
            self._log.error('%s: %s', type(_e).__name__, _e)
            self.pi.stop()
            raise _e

    def main(self):
        """ main """
        cmd_name = __class__.__name__
        prompt_str = f'\n{cmd_name}: [q] for exit > '
        cmd_exit = ('exit', 'quit', 'q', 'bye')

        print(f'[[ "{cmd_name}": Multipule Servo Motors Controller ]]')
        print(f' GPIO: {self.servo.pins}')
        print(f' conf_file: {self.servo.conf_file}')
        try:
            while True:
                in_str = input(prompt_str)
                self._log.debug('in_str="%s"', in_str)

                if in_str in cmd_exit:
                    break

                words = in_str.split()
                self._log.debug('words=%s', words)

                try:
                    angles = [float(word) for word in words]
                    self._log.debug('angles=%s', angles)

                    time_start = time.time()
                    self.servo.move_angle_sync(angles, self.sec)
                    time_end = time.time()

                    elapsed_time = time_end - time_start
                    moved_angles = self.servo.get_angle()
                    angles_str = ", ".join(
                        [f"{p:.0f}" for p in moved_angles]
                    )
                    angles_str = '[' + angles_str + ']'
                    print(f' {angles_str} ... {elapsed_time:.3f} sec')

                except ValueError as _e:
                    self._log.error('%s: %s', type(_e).__name__, _e)

        except (EOFError, KeyboardInterrupt) as _e:
            self._log.debug('%s: %s', type(_e).__name__, _e)

        except Exception as _e:
            self._log.error('%s: %s', type(_e).__name__, _e)

    def end(self):
        """ end """
        self._log.debug('')
        print('\n Bye!\n')
        self.servo.off()
        self.pi.stop()
