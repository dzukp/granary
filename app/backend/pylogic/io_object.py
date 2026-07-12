from .logged_object import LoggedObject
from .channel import Channel


class IoObject(LoggedObject):

    _save_attrs = ()

    def __init__(self, name='', parent=None):
        super(IoObject, self).__init__(name)
        self.children = []
        self.parent = None
        self.full_name = name
        self._set_parent(parent)
        self.saver = None

    # def __del__(self):
    #     if self.parent:
    #         self.parent.remove_child(self)
    #     for child in self.children:
    #         child.set_parent(self.parent)

    def set_saver(self, saver, include_children=True):
        self.saver = saver
        if include_children:
            for child in self.children:
                child.set_saver(saver, True)

    def add_child(self, child):
        self.children.append(child)
        #child.set_parent(self)

    def remove_child(self, child):
        try:
            self.children.remove(child)
        except ValueError:
            self.logger.error(f'`{self.name}` has no child `{child.name}`')

    def find_child_by_name(self, name):
        child_name = name.split('.')[0]
        child_child_name = '.'.join(name.split('.')[1:])
        for child in self.children:
            if child.name == child_name:
                if child_child_name:
                    grandchild = child.find_child_by_name(child_child_name)
                    if grandchild:
                        return grandchild
                else:
                    return child

    def _set_parent(self, parent):
        self.parent = parent
        if self.parent:
            self.full_name = '.'.join([parent.full_name, self.name])
            self.parent.add_child(self)
        else:
            self.full_name = self.name
        # for child in self.children:
        #     child.set_parent(self)

    def set_logger(self, logger):
        super().set_logger(logger)
        for child in self.children:
            child.set_logger(self.logger.getChild(child.name))

    def save(self):
        if self.saver:
            data = {}
            for attr in self._save_attrs:
                if hasattr(self, attr):
                    data[attr] = self.__dict__[attr]
            self.saver.save(self.full_name, data)

    def load(self):
        if self.saver:
            data = self.saver.load(self.full_name)
            if data:
                for name, value in data.items():
                    if hasattr(self, name):
                        self.__dict__[name] = value
                    else:
                        self.logger.error(f'Attribute `{name}` not exists')
                        self.__dict__[name] = value

    def load_all(self):
        self.load()
        for child in self.children:
            child.load_all()

    def save_all(self):
        self.save()
        for child in self.children:
            child.save()

    def get_all_channels(self):
        channels = [attr for name, attr in self.__dict__.items() if isinstance(attr, Channel)]
        for child in self.children:
            channels.extend(child.get_all_channels())
        return channels

    def init_all(self):
        try:
            self.init()
        except Exception:
            self.logger.exception(f'Undefined exception during child.process() name: {self.name}')
        for child in self.children:
            child.init_all()

    def init(self):
        pass

    def process_all(self):
        try:
            self.process()
        except Exception:
            self.logger.exception(f'Undefined exception during child.process() name: {self.name}')
        for child in self.children:
            child.process_all()

    def process(self):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}<{self.full_name}>'
