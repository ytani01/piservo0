#
# (c) 2025 Yoichi Tanibayashi
#
"""
mypkg
"""

from importlib.metadata import version

__version__ = version(__package__)

from .calibrable_servo import CalibrableServo
from .multi_servo import MultiServo
from .my_logger import get_logger
from .piservo import PiServo

__all__ = [
    "__author__",
    "__version__",
    "__prog_name__",
    "PiServo",
    "CalibrableServo",
    "MultiServo",
    "get_logger",
]
