import sys
from loguru import logger


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


logconfig = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <white>{message}</white>",
            "level": "INFO",
            "colorize": True,
            "filter": info_filter,
        },
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green>: <blue>{level}</blue> <red>{message}</red>",
            "level": "WARNING",
            "colorize": True,
            "filter": warn_filter,
        },
        {"sink": "ltools.log", "serialize": False},
    ],
}


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
