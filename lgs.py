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


def debug_filter(record):
    lvl = record["level"].name
    if lvl == "DEBUG":
        return False
    else:
        return False


def addlevel(ntwk):
    # logger.remove()
    s = "<cyan>%s</cyan> - <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <red>{level}</red> | <white>{message}</white>"% ntwk
    # s = "{message}"
    # logger.add(sys.stdout, level="WARNING", format=fmtstr)
    logger.add(sys.stdout, level="WARNING",format=s)

    # s= "<cyan>%s</cyan> - <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <blue>{level}</blue> | <white>{message}</white>"% ntwk
    # logger.add(sys.stdout, level="INFO", format=fmtstr, filter=info_filter)

    # logger.add(sys.stdout, level="DEBUG",format=fmtstr,filter=debug_filter)

    s= "<cyan>ZZ</cyan> - <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <blue>{level}</blue> | <white>{message}</white>"
    # logger.add("ltools.log", level="INFO", format=fmtstr, filter=info_filter)
    logger.add("ltools.log", level="INFO",format=s,filter=info_filter)


###global setup

import sys
import types

sys.modules["log"] = types.ModuleType("log")
import log

# addlevel("BSC")

log.info = logger.info
log.warning = logger.warning
log.debug = logger.debug


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
