import logging
from datetime import datetime
from typing import Optional

console_h: Optional[logging.StreamHandler] = None


def setup_log():
    global console_h
    logger = logging.getLogger('MCL')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    debugfile_fh = logging.FileHandler(f'debug_{s}.log', 'w')
    debugfile_fh.setLevel(logging.DEBUG)
    debugfile_fh.setFormatter(formatter)

    console_h = logging.StreamHandler()
    console_h.setLevel(logging.WARNING)
    console_h.setFormatter(formatter)

    logger.addHandler(debugfile_fh)
    logger.addHandler(console_h)


def set_console_log_level(lvl):
    if console_h is None:
        raise AttributeError("The logging system is not set-up!")
    console_h.setLevel(lvl)
