#
# (c) 2025 Yoichi Tanibayashi
#
import json
from .my_logger import get_logger
from .piservo import PiServo


class CalibrableServo(PiServo):
    """
    """
    DEF_CONF_FILE = './servo.json'

    def __init__(self, pi, pin,
            conf_file=DEF_CONF_FILE,
            debug=False):
        """
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug(f'pin={pin}')
        self._log.debug(f'conf_file={conf_file}')

        super().__init__(pi, pin, debug)

        self.conf_file = conf_file

        self.center = super().CENTER
        self.min = super().MIN
        self.max = super().MAX
        self._log.debug(
            f'center,min,max={self.center},{self.min},{self.max}'
        )

        res = self.load_conf()
        self._log.debug(f'res={res}')

        self.save_conf()

    def set_center(self, pulse):
        """
        """
        if pulse < super().MIN:
            self._log.warning(f'pulse({pulse}) < {super().MIN}')
            pulse = super().MIN

        if pulse > super().MAX:
            self._log.warning(f'pulse({pulse}) > {super().MAX}')
            pulse = super().MAX

        self._log.debug(f'pulse={pulse}')
        self.center = pulse

        self.save_conf()

        return self.center

    def set_min(self, pulse):
        """
        """
        if pulse < super().MIN:
            self._log.warning(f'pulse({pulse}) < {super().MIN}')
            pulse = super().MIN

        if pulse > super().MAX:
            self._log.warning(f'pulse({pulse}) > {super().MAX}')
            pulse = super().MAX

        self._log.debug(f'pulse={pulse}')
        self.min = pulse

        self.save_conf()

        return self.min

    def set_max(self, pulse):
        """
        """
        if pulse < super().MIN:
            self._log.warning(f'pulse({pulse}) < {super().MIN}')
            pulse = super().MIN

        if pulse > super().MAX:
            self._log.warning(f'pulse({pulse}) > {super().MAX}')
            pulse = super().MAX

        self._log.debug(f'pulse={pulse}')
        self.max = pulse

        self.save_conf()

        return self.max

    def move(self, pulse):
        """
        """
        self._log.debug(f'pin={self.pin},pulse={pulse}')

        if pulse < self.min:
            self._log.warning(f'pulse({pulse}) < self.min({self.min})')
            pulse = self.min

        if pulse > self.max:
            self._log.warning(f'pulse({pulse}) > self.max({self.max})')
            pulse = self.max

        self._log.debug(f'pulse={pulse}')
        super().move(pulse)

    def move_center(self):
        """
        """
        self._log.debug(f'pin={self.pin}')
        
        self.move(self.center)
        
    def move_min(self):
        """
        """
        self._log.debug(f'pin={self.pin}')
        
        self.move(self.min)
        
    def move_max(self):
        """
        """
        self._log.debug(f'pin={self.pin}')
        
        self.move(self.max)
        
    def read_jsonfile(self, conf_file=None):
        """
        """
        self._log.debug(f'conf_file={conf_file}')
        if conf_file is None:
            conf_file = self.conf_file
        self._log.debug(f'conf_file={conf_file}')

        data = []
        try:
            with open(conf_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._log.debug(f'data={data}')
                
        except Exception as e:
            self._log.error(f'{type(e).__name__}: {e}')

        return data

    def load_conf(self, conf_file=None):
        """
        """
        self._log.debug(f'conf_file={conf_file}')
        if conf_file is None:
            conf_file = self.conf_file
        self._log.debug(f'conf_file={conf_file}')

        # set default
        self.center, self.min, self.max = (
            super().CENTER, super().MIN, super().MAX
        )
        center, min, max = None, None, None

        data = self.read_jsonfile(conf_file)
        self._log.debug(f'data={data}')

        for pindata in data:
            if pindata['pin'] == self.pin:
                try:
                    center = pindata['center']
                except Exception as e:
                    self._log.warning(f'{type(e).__name__}: {e}')

                try:
                    min = pindata['min']
                except Exception as e:
                    self._log.warning(f'{type(e).__name__}: {e}')

                try:
                    max = pindata['max']
                except Exception as e:
                    self._log.warning(f'{type(e).__name__}: {e}')

                break

        self._log.debug(f'center,min,max={center},{min},{max}')

        if center is not None:
            self.center = center
        if min is not None:
            self.min = min
        if max is not None:
            self.max = max

        self._log.debug(f'self.center,self.min,self.max={self.center},{self.min},{self.max}')
        return self.center, self.min, self.max

    def save_conf(self, conf_file=None):
        """
        """
        self._log.debug(f'conf_file={conf_file}')
        if conf_file is None:
            conf_file = self.conf_file
        self._log.debug(f'conf_file={conf_file}')

        # read JSON data
        data = self.read_jsonfile(conf_file)
        self._log.debug(f'data={data}')

        # delete my element
        data = [pindata for pindata in data if pindata['pin'] != self.pin]
        self._log.debug(f'data={data}')

        # append my element
        data.append({
            'pin': self.pin,
            'center': self.center,
            'min': self.min,
            'max': self.max
        })
        self._log.debug(f'data={data}')

        # sort data
        data = sorted(data, key=lambda d: d['pin'])
        self._log.debug(f'data={data}')

        # write data
        try:
            with open(conf_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self._log.error(f'{type(e).__name__}: {e}')
