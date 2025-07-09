#
# (c) 2025 Yoichi Tanibayashi
#
"""
mypkg
"""
__author__ = 'Yoichi Tanibayashi'
__version__ = '0.0.1'

__prog_name__ = 'piservo0'

from .my_logger import get_logger
from .pigpio import PiGPIO

__all__ = [
    '__author__', '__version__', '__prog_name__',
    'PiGPIO',
    'get_logger'
]
