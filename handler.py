import logging
from random import randint


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.ip = ''
        return True


class StreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addFilter(ContextFilter())
