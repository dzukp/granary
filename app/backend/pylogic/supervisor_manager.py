from .logged_object import LoggedObject


class SupervisorManager(LoggedObject):
    """ Supervisor level manager """

    def __init__(self):
        super().__init__('Supervisors')
        self.top_object = None
        self.tag_srv = None
        self.supervisors = []

    def init(self):
        for supervisor in self.supervisors:
            supervisor.init()

    def set_top_object(self, top_object):
        self.top_object = top_object
        for supervisor in self.supervisors:
            supervisor.set_top_object(top_object)

    def set_tag_srv(self, tag_srv):
        self.tag_srv = tag_srv
        for supervisor in self.supervisors:
            supervisor.set_tag_srv(tag_srv)

    def add_supervisor(self, supervisor):
        self.supervisors.append(supervisor)
        supervisor.set_logger(self.logger.getChild(supervisor.name))

    def receive_data(self):
        self.logger.debug('Begin receive data')
        for supervisor in self.supervisors:
            supervisor.receive_data()
        self.logger.debug('End receive data')

    def send_data(self):
        self.logger.debug('Begin send data')
        for supervisor in self.supervisors:
            supervisor.send_data()
        self.logger.debug('End send data')


class BaseSupervisor(LoggedObject):

    def __init__(self, name):
        super().__init__(name)
        self.top_object = None
        self.tag_srv = None

    def init(self):
        pass

    def set_top_object(self, top_object):
        self.logger.debug('Set top object')
        self.top_object = top_object

    def set_tag_srv(self, tag_srv):
        self.logger.debug('Set tag server')
        self.tag_srv = tag_srv

    def receive_data(self):
        pass

    def send_data(self):
        pass
