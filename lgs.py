"""
WIP logging per ntwk
"""
import sys
from loguru import logger

import sys
import types

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



# def make_info_handler(ntwk):
#     # print("make_info_handler ", ntwk)
#     fmt = "%s>>>> <green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>"%ntwk
#     return {
#         "sink": sys.stdout,
#         "format": fmt,
#         "level": "INFO",
#         "colorize": True,
#         "filter": info_filter,
#     }


# def make_warn_handler(ntwk):
#     fmt = "%s>>>> <green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>"%ntwk
#     return {
#         "sink": sys.stdout,
#         "format": fmt,
#         # "format": WarnFormatter(ntwk).format,
#         "level": "WARNING",
#         "colorize": True,
#         "filter": info_filter,
#     }


# def get_config(XX):
#     return {
#         "handlers": [
#             make_info_handler("XX"),
#             # make_warn_handler(ntwk),
#             {"sink": "ltools.log", "serialize": False},
#         ],
#     }

def addlevel(ntwk):
    logger.remove()
    # logger.add(sys.stdout, level="DEBUG",format="?? - {message}")
    fmtstr = "<cyan>%s</cyan> - <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <red>{level}</red> | <white>{message}</white>"%ntwk
    # logger.add(sys.stdout, level="WARNING",format="%s - {message}"%ntwk)
    logger.add(sys.stdout, level="WARNING",format=fmtstr,filter=warn_filter)

    fmtstr = "<cyan>%s</cyan> - <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <blue>{level}</blue> | <white>{message}</white>"%ntwk
    logger.add(sys.stdout, level="INFO",format=fmtstr,filter=info_filter)

    logger.add("ltools.log", level="INFO",format=fmtstr,filter=info_filter)

###setup

print("setup..")
import sys
import types
sys.modules["log"] = types.ModuleType("log")
import log
log.info = logger.info
log.warning = logger.warning



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
