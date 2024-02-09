import logging
import sys
from os import getenv


# https://stackoverflow.com/a/31688396/23112474
class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != "\n":
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        self.level(sys.stderr)


class Logger:
    def __init__(self, name: str):
        self.log = logging.getLogger(name)
        if getenv("DEBUG"):
            logging.basicConfig(filename=".log", encoding="utf-8", level=logging.DEBUG)
            sys.stdout = LoggerWriter(self.log.debug)
        else:
            logging.basicConfig(filename=".log", encoding="utf-8", level=logging.INFO)
            sys.stdout = LoggerWriter(self.log.info)
        sys.stderr = LoggerWriter(self.log.warning)

    def debug(self, message: str):
        self.log.debug(message)

    def info(self, message: str):
        self.log.info(message)

    def warning(self, message: str):
        self.log.warning(message)

    def error(self, message: str):
        self.log.error(message)
