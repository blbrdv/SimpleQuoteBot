import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from os import getenv


class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if getenv("DEBUG"):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        formater = logging.Formatter("%(name)-13s: %(levelname)-8s %(message)s")

        file_handler = TimedRotatingFileHandler(
            ".log", when="d", interval=1, backupCount=30
        )
        file_handler.setFormatter(formater)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formater)
        self.logger.addHandler(stream_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
