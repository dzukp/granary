

class Channel:
    def __init__(self, value=0):
        if type(self) == Channel:
            raise Exception('Channel is an abstact class, use inherited class')
        self._name = ''
        self.trans = None
        self._value = value

    def set_name(self, name):
        self._name = name

    def set_trans(self, trans):
        self.trans = trans

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f'"{self.name}":{self._value}'


class InChannel(Channel):

    def set_value(self, value):
        ''' For TagSrv using only '''
        if self.trans:
            self._value = self.trans(value)
        else:
            self._value = value

    @property
    def val(self):
        return self._value


class OutChannel(Channel):

    def get_value(self):
        ''' For TagSrv using only '''
        if self.trans:
            return self.trans(self._value)
        return self._value

    @property
    def val(self):
        return self._value

    @val.setter
    def val(self, value):
        self._value = value


class InOutChannel(Channel):

    def set_value(self, value):
        ''' For TagSrv using only '''
        if self.trans:
            self._value = self.trans(value)
        else:
            self._value = value

    def get_value(self):
        ''' For TagSrv using only '''
        if self.trans:
            return self.trans(self._value)
        return self._value

    @property
    def val(self):
        return self._value

    @val.setter
    def val(self, value):
        self._value = value
