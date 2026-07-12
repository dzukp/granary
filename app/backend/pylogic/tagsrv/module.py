
class BaseModule(object):

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.ok = False
        self.last_ok = 0
        self.tags = []

    def process(self):
        pass

    def tag_values(self):
        return [self._value_to_str(t.value) for t in self.tags]

    def _value_to_str(self, value):
        return str(value)
