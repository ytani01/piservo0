#
# (c) 2025 Yoichi Tanibayashi
#
import time

from .calibrable_servo import CalibrableServo
from .my_logger import get_logger
from .piservo import PiServo


class CmdCalib:
    """calibration tool"""

    def __init__(self, pi, pin, conf_file, sec=1.0, debug=False):
        self._debug = debug
        self.__log = get_logger(__class__.__name__, self._debug)
        self.__log.debug("pin=%s,conf_file=%s,sec=%s", pin, conf_file, sec)

        self.pin = pin
        self.conf_file = conf_file
        self.sec = sec

        self.pi = pi
        if not self.pi.connected:
            self.__log.error("pigpio daemon not connected.")
            raise ConnectionError("pigpio daemon not connected.")

        try:
            self.servo = CalibrableServo(
                self.pi, self.pin, conf_file=self.conf_file, debug=self._debug
            )
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            self.pi.stop()
            raise _e

    def main(self, ctx):
        """main"""
        cmd_name = ctx.command.name

        prompt_str = f"\n{cmd_name}: [h] for help, [q] for exit > "

        cmd_center = {"help": "move center", "str": ("center", "c")}
        cmd_angle = {"help": "move angle", "str": "-90.0 .. 0.0 .. 90.0"}
        cmd_pulse = {"help": "move pulse", "str": "500 .. 2500"}
        cmd_min = {"help": "move min", "str": ("min", "n")}
        cmd_max = {"help": "move max", "str": ("max", "x")}
        cmd_get = {"help": "get pulse", "str": ("get pulse", "get", "g")}
        cmd_set_center = {"help": "set center", "str": ("set center", "sc")}
        cmd_set_min = {"help": "set min", "str": ("set min", "sn")}
        cmd_set_max = {"help": "set max", "str": ("set max", "sx")}
        cmd_save = {"help": "save config", "str": ("save", "s")}  # 追加
        cmd_exit = {"help": "exit", "str": ("exit", "quit", "q", "bye")}
        cmd_help = {"help": "help", "str": ("help", "h", "?")}

        cmds = [
            cmd_angle,
            cmd_pulse,
            cmd_center,
            cmd_min,
            cmd_max,
            cmd_get,
            cmd_set_center,
            cmd_set_min,
            cmd_set_max,
            cmd_save,  # 追加
            cmd_help,
            cmd_exit,
        ]

        print(f'\n[[ "{cmd_name}": Servo Calibration Tool ]]\n')
        print(f" GPIO: {self.servo.pin}")
        print(f" conf_file: {self.servo.conf_file}")

        angle_min = CalibrableServo.ANGLE_MIN
        angle_max = CalibrableServo.ANGLE_MAX
        pulse_min = PiServo.MIN
        pulse_max = PiServo.MAX

        try:
            while True:
                in_str = input(prompt_str)
                self.__log.debug("in_str=%s", in_str)

                # 数値が入力されたか？
                try:
                    val = float(in_str)

                    # 角度として入力されたか？
                    if angle_min <= val <= angle_max:
                        self.servo.move_angle(val)
                        pulse = self.servo.get_pulse()
                        print(f" angle = {val}, pulse={pulse}")
                        time.sleep(self.sec)
                        continue

                    # パルス幅として入力されたか？
                    if pulse_min <= val <= pulse_max:
                        self.servo.move_pulse(int(round(val)), forced=True)
                        pulse = self.servo.get_pulse()
                        print(f" pulse = {pulse}")
                        time.sleep(self.sec)
                        continue

                    self.__log.error("%s: out of range", val)
                    continue

                except ValueError:
                    # 文字列が入力された
                    pass

                if in_str in cmd_help["str"]:
                    print("\nUSAGE\n")

                    for cmd in cmds:
                        s_cmds = ""
                        if isinstance(cmd["str"], str):
                            s_cmds = cmd["str"]
                        else:
                            for s in cmd["str"]:
                                s_cmds += f'"{s}", '
                            s_cmds = s_cmds[:-2]
                        print(f" {s_cmds:28} {cmd['help']:12}")

                    continue

                if in_str in cmd_center["str"]:
                    self.servo.move_center()
                    pulse = self.servo.get_pulse()
                    print(f" center: pulse={pulse}")
                    time.sleep(self.sec)
                    continue

                if in_str in cmd_min["str"]:
                    self.servo.move_min()
                    pulse = self.servo.get_pulse()
                    print(f" min: pulse={pulse}")
                    time.sleep(self.sec)
                    continue

                if in_str in cmd_max["str"]:
                    self.servo.move_max()
                    pulse = self.servo.get_pulse()
                    print(f" max: pulse={pulse}")
                    time.sleep(self.sec)
                    continue

                if in_str in cmd_get["str"]:
                    pulse = self.servo.get_pulse()
                    print(f" pulse = {pulse}")
                    print(
                        f" min={self.servo.pulse_min}, "
                        f"center={self.servo.pulse_center}, "
                        f"max={self.servo.pulse_max}"
                    )
                    continue

                if in_str in cmd_set_center["str"]:
                    pulse = self.servo.get_pulse()
                    self.servo.pulse_center = pulse
                    print(f" set center: pulse = {pulse}")
                    print(f" file: {self.servo.conf_file}")
                    continue

                if in_str in cmd_set_min["str"]:
                    pulse = self.servo.get_pulse()
                    self.servo.pulse_min = pulse
                    print(f" set min: pulse = {pulse}")
                    print(f" file: {self.servo.conf_file}")
                    continue

                if in_str in cmd_set_max["str"]:
                    pulse = self.servo.get_pulse()
                    self.servo.pulse_max = pulse
                    print(f" set max: pulse = {pulse}")
                    print(f" file: {self.servo.conf_file}")
                    continue

                if in_str in cmd_save["str"]:
                    self.servo.save_conf()
                    print(f" Configuration saved to {self.servo.conf_file}")
                    continue

                if in_str in cmd_exit["str"]:
                    break

                self.__log.error("%s: invalid command", in_str)

        except (EOFError, KeyboardInterrupt) as _e:
            self.__log.debug("%s: %s", type(_e).__name__, _e)

    def end(self):
        """end"""
        self.__log.debug("")
        print("\n Bye!\n")
        self.servo.off()
