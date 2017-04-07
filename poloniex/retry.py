# http://code.activestate.com/recipes/580745-retry-decorator-in-python/
from itertools import chain
from time import sleep
import logging
logger = logging.getLogger(__name__)


def retry(delays=(0, 1, 5, 30),
          exception=Exception):
    def wrapper(function):
        def wrapped(*args, **kwargs):
            problems = []
            for delay in chain(delays, [None]):
                try:
                    return function(*args, **kwargs)
                except exception as problem:
                    problems.append(problem)
                    if delay is None:
                        logger.error(problems)
                        raise
                    else:
                        logger.debug(problem)
                        logger.info("-- delaying for %ds", delay)
                        sleep(delay)
        return wrapped
    return wrapper
