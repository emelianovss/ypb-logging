import os
import asyncio
import logging
import logging.config
import argparse
import sentry_sdk
from random import randint
from sentry_sdk.integrations.logging import LoggingIntegration


MAX_DELAY_SECONDS = 5
parent_logger = logging.getLogger('parent')
children_logger = logging.getLogger('parent.children')
logging.config.fileConfig('logging.ini')


async def sleep():
    await asyncio.sleep(randint(1, MAX_DELAY_SECONDS))


async def debug(event: 'asyncio.Event'):
    while not event.set():
        parent_logger.debug('Debug message')
        children_logger.debug('Debug message')
        await sleep()


async def info(event: 'asyncio.Event'):
    while not event.set():
        parent_logger.info('Info message')
        children_logger.info('Info message')
        await sleep()


async def warning(event: 'asyncio.Event'):
    while not event.set():
        parent_logger.warning('Warning message')
        children_logger.warning('Warning message')
        await sleep()


async def error(event: 'asyncio.Event'):
    while not event.set():
        parent_logger.error('Error message')
        children_logger.warning('Error message')
        await sleep()


async def exception(event: 'asyncio.Event'):
    while not event.set():
        try:
            _ = {}['key']
        except KeyError:
            parent_logger.exception('Exception message')

        try:
            _ = {}['key']
        except KeyError:
            children_logger.exception('Exception message')
        await sleep()


def create_tasks(loop, event, exception_enable):
    sentry_dsn = os.environ.get('SENTRY_DSN', None)
    if sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        sentry_sdk.init(sentry_dsn, traces_sample_rate=1.0, integrations=[sentry_logging])
    functions = [debug, info, warning, error]
    if exception_enable:
        functions.append(exception)
    [loop.create_task(func(event)) for func in functions]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ex_enable', action='store_true', required=False)
    logging.info('Start application')
    current_loop = asyncio.get_event_loop()
    signal_event = asyncio.Event()
    args = parser.parse_args()
    create_tasks(current_loop, signal_event, args.ex_enable)
    try:
        current_loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Wait stop application')
        signal_event.set()
        current_loop.stop()
        logging.info('Application success stop')
