"""
WIP logging per ntwk
"""
import sys
from loguru import logger

import sys
import types

sys.modules["logo"] = types.ModuleType("logo")


def info_filter(record):
    lvl = record["level"].name
    if lvl == "INFO":
        return True
    elif lvl == "WARNING":
        return False


def warn_filter(record):
    lvl = record["level"].name
    if lvl == "INFO":
        return False
    elif lvl == "WARNING":
        return True


class InfoFormatter:
    def __init__(self, ntwk):
        self.ntwk = ntwk
        # self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"
        self.fmt = "{extra[network]} | <green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>\n"

    def format(self, record):
        # length = len("{name}:{function}:{line}".format(**record))
        # self.padding = max(self.padding, length)
        record["extra"]["network"] = self.ntwk
        return self.fmt


class WarnFormatter:
    def __init__(self, ntwk):
        self.ntwk = ntwk
        # self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"
        self.fmt = "{extra[network]} | <green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <red>{message}</red>\n"

    def format(self, record):
        # length = len("{name}:{function}:{line}".format(**record))
        # self.padding = max(self.padding, length)
        record["extra"]["network"] = self.ntwk
        return self.fmt


def make_info_handler(ntwk):
    print("make_info_handler ", ntwk)
    fmt = InfoFormatter(ntwk).format
    print(fmt)
    return {
        "sink": sys.stdout,
        # "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>",
        "format": fmt,
        "level": "INFO",
        "colorize": True,
        "filter": info_filter,
    }


def make_warn_handler(ntwk):
    return {
        "sink": sys.stdout,
        # "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>",
        "format": WarnFormatter(ntwk).format,
        "level": "INFO",
        "colorize": True,
        "filter": info_filter,
    }


def get_config(ntwk):
    return {
        "handlers": [
            make_info_handler(ntwk),
            make_warn_handler(ntwk),
            {"sink": "ltools.log", "serialize": False},
        ],
    }


###setup

print("setup..")
import sys
import types

sys.modules["log"] = types.ModuleType("log")

# import log

# logger.add(sys.stdout, format="?? {extra[ip]} - {message}")
fmtstr = "<red>{extra[ntwk]}</red> - <green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>"
logger.add(sys.stdout, format=fmtstr)


class Loglevel:
    def __init__(self, ntwk):
        self.ntwk = ntwk
        self.logger = logger.bind(ntwk=ntwk)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)


# logcfg = get_config("XX")
# print (logcfg)
# logger.configure(**logcfg)
# log.info = logger.info
# log.warn = logger.warning

# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         print ("emit ",record )
#         # Get corresponding Loguru level if it exists
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno

#         # Find caller from where originated the logged message
#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1

#         logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
# logging.basicConfig(handlers=[InterceptHandler()], level=0)
