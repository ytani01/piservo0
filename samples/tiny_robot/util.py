#
# (c) 2025 Yoichi Tanibayashi
#
import time

from piservo0 import get_logger


class Util:
    """utility functions"""

    # SEQの角度をサーボに与える実際の角度に変換するための係数
    #                  [FL, BL, BR, FR]
    DEF_ANGLE_FACTOR = [-1, -1, 1, 1]

    # angle文字
    CH_CENTER = "c"
    CH_MIN = "n"
    CH_MAX = "x"
    CH_FORWARD = "f"
    CH_BACKWARD = "b"
    CH_DONT_MOVE = "."

    ANGLE_CHS = [
        CH_CENTER,
        CH_MIN,
        CH_MAX,
        CH_FORWARD,
        CH_BACKWARD,
        CH_DONT_MOVE,
    ]

    def __init__(
        self,
        mservo,
        move_sec,
        angle_unit,
        angle_factor=DEF_ANGLE_FACTOR,
        debug=False,
    ):
        """constructor"""
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug(
            "move_sec=%s,angle_unit=%s,angle_factor=%s",
            move_sec,
            angle_unit,
            angle_factor,
        )

        self.mservo = mservo
        self.move_sec = move_sec
        self.angle_unit = angle_unit
        self.angle_factor = angle_factor

    def clip(self, v, v_min, v_max):
        """min <= v <= max"""
        self._log.debug("v=%s,min=%s,max=%s", v, v_min, v_max)

        return max(min(v, v_max), v_min)

    def set_move_sec(self, move_sec):
        """ """
        self.move_sec = move_sec

    def set_angle_unit(self, angle: float) -> float:
        """ """
        self._log.debug("angle=%s", angle)

        if angle <= 0:
            return -1

        self.angle_unit = angle

        return self.angle_unit

    def is_anglecmd(self, cmd):
        """ """
        if len(cmd) != 4:
            self._log.debug("cmd=%s: False", cmd)
            return False

        cmd = cmd.lower()

        for _ch in cmd:
            if _ch not in self.ANGLE_CHS:
                self._log.debug("cmd=%s:_ch=%s: False", cmd, _ch)
                return False

        self._log.debug("cmd=%s: True", cmd)
        return True

    def is_float_str(self, s):
        """ """
        self._log.debug("s=%s", s)

        try:
            float(s)
            return True
        except ValueError:
            return False

    def parse_cmd(self, cmd):
        """parse cmdline

        e.g.
          self.angle_unit = 40
          self.angle_factor = [-1, -1, 1, 1]

          'FBCF' --> {'angles', [-40, 40, 0, 40]}

        """
        self._log.debug("cmd=%s", cmd)

        ret = None

        if self.is_anglecmd(cmd):
            angles = []

            for _i, _ch in enumerate(cmd):
                _af = self.angle_factor[_i]

                # if upper case, double angle
                if _ch.isupper():
                    _af *= 2
                    _ch = _ch.lower()

                _angle = None

                if _ch == self.CH_CENTER:
                    _angle = 0

                elif _ch == self.CH_MIN:
                    _angle = -90 * _af

                elif _ch == self.CH_MAX:
                    _angle = 90 * _af

                elif _ch == self.CH_FORWARD:
                    _angle = self.angle_unit * _af

                elif _ch == self.CH_BACKWARD:
                    _angle = self.angle_unit * _af * -1

                elif _ch == self.CH_DONT_MOVE:
                    _angle = self.mservo.servo[_i].get_angle()

                if _angle is not None:
                    _angle = self.clip(_angle, -90, 90)
                    angles.append(_angle)

            self._log.debug("angles=%s", angles)

            ret = {"cmd": "angles", "angles": angles}

        elif self.is_float_str(cmd):
            ret = {"cmd": "interval", "sec": float(cmd)}

        else:
            ret = {"cmd": "error", "err": "invalid command"}

        self._log.debug("ret=%s", ret)
        return ret

    def exec_cmd(self, cmd):
        """ """
        res = self.parse_cmd(cmd)

        if res["cmd"] == "angles":
            angles = res["angles"]
            self.mservo.move_angle_sync(angles, self.move_sec)
            return

        if res["cmd"] == "interval":
            time.sleep(float(res["sec"]))
            return

        # else: Error
        print(f'ERROR:"{cmd}": {res["cmd"]}, {res["err"]}')

    def flip_angle_strs(self, strs):
        """
        'fcbx' --> 'xbcf'
        '0.5' --> '0.5'
        """
        new_strs = []
        for _s in strs:
            self._log.debug("_s=%s", _s)

            _new_s = _s
            if self.is_anglecmd(_s):
                _new_s = _s[::-1]
            self._log.debug("_new_s=%s", _new_s)

            new_strs.append(_new_s)

        return new_strs

    def flip_lists(self, lists):
        """Flip the lists

        e.g.
          from
          [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
          ]

          to
          [
            [4, 3, 2, 1],
            [8, 7, 6, 5],
          ]
        """
        self._log.debug("lists =")
        for _c in lists:
            self._log.debug("  %s", _c)

        new_lists = []
        for c in lists:
            c.reverse()
            new_lists.append(c)

        self._log.debug("new_lists =")
        for _c in new_lists:
            self._log.debug("  %s", _c)

        return new_lists
