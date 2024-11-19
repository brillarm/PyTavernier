from __future__ import annotations

from datetime import timedelta
from logging import Handler, LogRecord
from os import environ
from pprint import pformat
from sys import stderr, stdout

import loguru
from loguru import logger

from .settings import SETTINGS

logger.remove(0)  # remove the pre-configured handler

STDOUT_MAX_LVL = logger.level(SETTINGS.LOGGER_MAX_LVL).no
DIAG = True if SETTINGS.ENV == "DEV" else False
ENQUEUE = False


def isColorSupported():
    if not stdout.isatty():  # vérifie que le terminal est interactif
        return False
    # vérifie que le terminal supporte les couleurs
    term = environ.get("TERM", "")
    return "color" in term or "ansi" in term


def filterStdout(record: loguru.Record) -> bool:
    if filter_discord(record):  # dont get logs from discord
        return False
    if record["level"].no > STDOUT_MAX_LVL:
        return False
    return True


def filter_discord(record: loguru.Record) -> bool:
    if "is_from_discord" in record["extra"].keys():
        return True
    return False


def create_filtered_sinks() -> None:
    LVL_FILES = {
        "logs/trace.log": "TRACE",
        "logs/debug.log": "DEBUG",
        "logs/info.log": "INFO",
        "logs/success.log": "SUCCESS",
        "logs/error.log": "ERROR",
        "logs/critical.log": "CRITICAL",
    }
    for file, name in LVL_FILES.items():

        def filter_func(record: loguru.Record, level: str = name):
            return record["level"].name == level

        logger.add(
            sink=file,
            format=FMT,
            filter=filter_func,
            colorize=False,
            enqueue=ENQUEUE,
            rotation=timedelta(days=7),
        )


class DiscordLoguruHandler(Handler):
    def __init__(self, level=0):
        Handler.__init__(self, level)

    def emit(self, record: LogRecord):
        # This will forward records from the `logging` module to `loguru`
        loguru_level = (
            logger.level(record.levelname).name
            if record.levelname in logger._core.levels
            else record.levelno
        )
        logger.patch(lambda record: record["extra"].update(is_from_discord=True)).log(
            loguru_level,
            pformat(
                record.getMessage(),
                indent=4,
                compact=True,
                sort_dicts=True,
            ),
        )

    def setFormatter(self, *any):
        return


FMT = "[<lk>{time:DD/MM/YYYY} {time:HH:mm:ss.SSS}</lk>] <lvl>{level:8}</lvl> [<cyan>{file}</cyan>:<y>{line}</y>] (<e>{function}</e>) : <lvl>{message}</lvl>"

logger.add(
    sink="logs/all.log",
    format=FMT,
    level="TRACE",
    colorize=False,
    enqueue=ENQUEUE,
    diagnose=DIAG,
    rotation=timedelta(days=1),
)
logger.add(
    sink="logs/discord.log",
    format=FMT,
    filter=filter_discord,
    level="TRACE",
    colorize=False,
    enqueue=ENQUEUE,
    diagnose=DIAG,
    rotation=timedelta(days=1),
)
create_filtered_sinks()  # creates a sink for each log level

logger.add(
    sink=stdout,
    format=FMT,
    level=SETTINGS.LOGGER_LVL,
    filter=filterStdout,
    colorize=True,
    enqueue=ENQUEUE,
    diagnose=DIAG,
)
logger.add(
    sink=stderr,
    format=FMT,
    level="ERROR",
    colorize=True,
    enqueue=ENQUEUE,
    diagnose=DIAG,
)


def test():
    logger.trace("trace test")
    logger.debug("debug test")
    logger.info("info test")
    logger.success("success test")
    logger.error("error test")
    logger.critical("critical test")
    try:
        1 / 0
    except Exception as e:
        logger.exception("exception test", e)


if __name__ == "__main__":
    test()
