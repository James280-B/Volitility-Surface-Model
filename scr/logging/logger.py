import logging


class Logger:
    def __init__(self):
        self.logger = logging.getLogger("SimpleLogger")
        self.file_handler = logging.FileHandler("output.log")

    def record(self):
        pass
