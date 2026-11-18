import logging
import os

from scr.utils.env_utils import read_environment_variables


def setup_logger(level=logging.INFO):
    log_dir = os.path.join(read_environment_variables("LOG_PATH"), "logs.log")
    print("Logging to {}".format(log_dir))
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', handlers=[logging.StreamHandler(), logging.FileHandler(log_dir)])
