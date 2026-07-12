import time


__all__ = ('default_periodic_clock', 'Timer', 'Ton')


class PeriodicClock:
    def __init__(self):
        self.current_time = time.time()

    def update(self):
        self.current_time = time.time()

    def time(self):
        return self.current_time


class MomentClock:
    def time(self):
        return time.time()


default_periodic_clock = PeriodicClock()

periodic_clocks = {
    'default': default_periodic_clock
}

moment_clock = MomentClock()


def get_periodic_clock(name):
    if name not in periodic_clocks:
        periodic_clocks[name] = PeriodicClock()
    return periodic_clocks[name]


class Timer:

    def __init__(self, periodic_clock_name='default', moment_clock_name=False):
        if periodic_clock_name:
            self.clock = get_periodic_clock(periodic_clock_name)
        elif moment_clock_name:
            self.clock = moment_clock
        else:
            raise Exception('need use periodic_clock or moment_clock')
        self.started = False
        self.timeout = 0.0
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def start(self, timeout=None):
        if timeout is not None:
            self.timeout = timeout
        if not self.started:
            self.started = True
            self.start_time = self.clock.time()
            self.end_time = self.start_time + self.timeout

    def reset(self):
        self.started = False
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0

    def restart(self):
        self.reset()
        self.start()

    def left(self):
        return self.end_time - self.clock.time()

    def elapsed(self):
        return self.clock.time() - self.start_time

    def is_end(self):
        return self.end_time < self.clock.time()


class Ton:
    """Таймер задержкм включения"""
    def __init__(self, periodic_clock_name='default', moment_clock_name=False):
        if periodic_clock_name:
            self.clock = get_periodic_clock(periodic_clock_name)
        elif moment_clock_name:
            self.clock = moment_clock
        else:
            raise Exception('need use periodic_clock or moment_clock')
        self._started = False
        self._start_time = 0
        self._timeout = 0.0

    def process(self, run, timeout=None):
        if timeout is not None:
            self._timeout = timeout
        if self._started and not run:
            self.reset()
        elif not self._started and run:
            self._start_time = self.clock.time()
            self._started = True
        if self._started and self._start_time + self._timeout < self.clock.time():
            return True
        return False

    def reset(self):
        self._started = False
        self._start_time = 0

    def set_timeout(self, timeout):
        self._timeout = timeout