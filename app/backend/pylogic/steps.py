from .logged_object import LoggedObject


class Steps(LoggedObject):
    """ Steps container """

    def __init__(self, name='', *args, **kwargs):
        super().__init__(name)
        self.args = args
        self.kwargs = kwargs
        self.current_step = self.idle
        self.trans_args = []

    def idle(self):
        pass

    def step_first(self):
        """ Begin step, need implementatin """
        pass

    def process(self):
        cs = self.current_step(*self.trans_args)
        if cs:
            if isinstance(cs, (tuple, list)):
                self.current_step = cs[0]
                self.trans_args = cs[1:]
            elif callable(cs):
                self.current_step = cs
                self.trans_args = ()
            else:
                raise Exception('Return value of the logic step must be are dict or func')
            self.logger.info(f'New step: {self.current_step.__name__}')

    def start(self):
        if self.is_idle():
            self.current_step = self.step_first
            self.trans_args = []
            self.logger.info(f'Start')

    def stop(self):
        if not self.is_idle():
            self.current_step = self.idle
            self.trans_args = []
            self.logger.info(f'Stop')

    def is_idle(self):
        return self.current_step == self.idle