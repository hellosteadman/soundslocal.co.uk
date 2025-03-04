from logging import getLogger


logger = getLogger('budgie')


def debug(message: str):
    logger.debug(message)


def error(ex: Exception):
    logger.error(ex, exc_info=True)
