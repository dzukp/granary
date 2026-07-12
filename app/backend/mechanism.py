from pylogic.io_object import IoObject


class Mechanism(IoObject):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.next_mechanisms: list[Mechanism] = []

    def is_running(self):
        raise NotImplementedError

    def check_next_mechanisms(self):
        if not self.next_mechanisms:
            return True
        for mech in self.next_mechanisms:
            if mech.is_running():
                return True
        return False

    def disable(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError


class MechManager:

    def disable(self):
        for child in self.children:
            if isinstance(child, Mechanism):
                child.disable()

    def enable(self):
        for child in self.children:
            if isinstance(child, Mechanism):
                child.enable()

    def is_running(self):
        return any(mech.is_running() for mech in self.children)
