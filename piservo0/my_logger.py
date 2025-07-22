#
# Copyright (c) 2020 Yoichi Tanibayashi
#
"""
my_logger.py
"""

__author__ = "Yoichi Tanibayahashi"
__date__ = "2021"

import inspect
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
# from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL


def get_logger(name, debug=False):
    """
    get logger
    """
    filename = inspect.stack()[1].filename.split("/")[-1]
    name = filename + "." + name
    logger = getLogger(name)
    logger.propagate = False  # Prevent messages from being passed to the root logger

    # Clear existing handlers to prevent duplicates if get_logger is called multiple times for the same name
    if logger.handlers:
        logger.handlers.clear()

    # Create a new handler and formatter for each logger
    fmt_hdr = "%(asctime)s %(levelname)s "
    fmt_loc = "%(name)s.%(funcName)s:%(lineno)d> "
    handler_fmt = Formatter(fmt_hdr + fmt_loc + "%(message)s", datefmt="%H:%M:%S")

    console_handler = StreamHandler()
    console_handler.setFormatter(handler_fmt)
    console_handler.setLevel(
        DEBUG
    )  # Set handler level to DEBUG to allow all messages through

    logger.addHandler(console_handler)

    logger.setLevel(INFO)  # Default logger level

    # [Important !! ]
    # isinstance()では、boolもintと判定されるので、
    # 先に bool かどうかを判定する

    if isinstance(debug, bool):
        if debug:
            logger.setLevel(DEBUG)
        return logger

    if isinstance(debug, int):
        logger.setLevel(debug)
        return logger

    raise ValueError("invalid `debug` value: %s" % (debug))
