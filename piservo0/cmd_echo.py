import time
from piservo0 import get_logger


class CmdEcho:
    """  """
    def __init__(self, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)

    def main(self):
        """  """
        self._log.debug('')

        str_list = ["this", "is", "sample", "command"]

        for _s in str_list:
            print(f'{_s} ' , end="", flush=True)
            time.sleep(1)

        print()

    def end(self):
        """  """
        self._log.debug('')
        
        print('bye!')
