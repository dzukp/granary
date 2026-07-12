import logging


__all__ = ['LoggedObject', 'DEFAULT_LOGGER']


DEFAULT_LOGGER = 'PylogicLogger'


class LoggedObject(object):

    def __init__(self, name=None):
        if name is None:
            name = _gen_name()
        self.name = name
        self.logger = logging.getLogger(DEFAULT_LOGGER)

    def set_logger(self, logger):
        self.logger = logger


_last_idx = 1


def _gen_name():
    global _last_idx
    new_name = f'_{str(_last_idx).zfill(4)}'
    _last_idx += 1
    return new_name
