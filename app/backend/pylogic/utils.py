
class Hysteresis:
    """
        Hysteresis heater
        If value > hi -> process() return False
        If value < low -> process() return True
    """
    def __init__(self, low, hi):
        self.low = low
        self.hi = hi
        self._on = False
        self._switch = False

    def process(self, value):
        self._switch = False
        if value > self.hi:
            if not self._on:
                self._switch = True
            self._on = True
        elif value < self.low:
            if self._on:
                self._switch = True
            self._on = False
        return self._on

    def isSwitchToOn(self):
        return self._switch and self._on

    def isSwitchToOff(self):
        return self._switch and not self._on