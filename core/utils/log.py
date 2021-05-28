import logging
from datetime import datetime


def setup_log():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    debugfile_fh = logging.FileHandler(f'debug_{s}.log', 'w')
    debugfile_fh.setLevel(logging.DEBUG)
    debugfile_fh.setFormatter(formatter)

    console_h = logging.StreamHandler()
    console_h.setLevel(logging.WARNING)
    console_h.setFormatter(formatter)

    logger.addHandler(debugfile_fh)
    logger.addHandler(console_h)
