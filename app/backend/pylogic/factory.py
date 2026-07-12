from pylogic.logged_object import LoggedObject
from pylogic.controller import Controller
from pylogic.tagsrv.tagsrv import TagSrv
from pylogic.channel import Channel
from pylogic.saver import FileParameterSaver
from pylogic.supervisor_manager import SupervisorManager

import logging


class Factory(LoggedObject):

    def __init__(self):
        super().__init__('Factory')
        self.controller = None
        self.tag_srv = None
        self.top_object = None
        self.saver = None
        self.supervisor_manager = None
        self.controller_class = Controller
        self.tagsrv_class = TagSrv
        self.saver_class = FileParameterSaver
        self.supervisor_manager_class = SupervisorManager

    def get_controller(self):
        if self.controller is None:
            self.logger.info('Create controller')
            self.controller = self.controller_class()
        return self.controller

    def get_tag_srv(self, tagsrv_config, channels, simulators):
        if self.tag_srv is None:
            self.logger.info('Create tag server')
            self.tag_srv = self.tagsrv_class()
            self.tag_srv.init(tagsrv_config, channels, simulators)
        return self.tag_srv

    def get_top_object(self, config):
        if self.top_object is None:
            self.logger.info('Create io objects')
            if len(config) != 1:
                raise Exception('Required 1 root io_object')
            for name, cfg in config.items():
                self.top_object = self.io_object_config_parse(name, cfg, None)
        return self.top_object

    def get_simulator_object(self, config):
        self.logger.info('Create simulator objects')
        if len(config) > 1:
            raise Exception('Required 1 root io_object')
        for name, cfg in config.items():
            simulator = self.io_object_config_parse(name, cfg, None)
            return simulator

    def io_object_config_parse(self, name, config, parent):
        current = config['class'](name, parent)
        current.set_logger(parent.logger.getChild(current.name) if parent is not None else logging.getLogger(name))
        for key, value in config.items():
            if key in ('class', 'children'):
                pass
            elif hasattr(current, key):
                if isinstance(current.__dict__[key], Channel):
                    current.__dict__[key].set_name(value)
                else:
                    current.__dict__[key] = value
        if 'children' in config:
            for child_name, child_cfg in config['children'].items():
                child = self.io_object_config_parse(child_name, child_cfg, current)
            for key, value in current.__dict__.items():
                if value is None and key in config['children']:
                    current.__dict__[key] = current.find_child_by_name(key)
        return current

    def get_saver(self):
        if self.saver is None:
            self.saver = self.saver_class()
            self.saver.set_logger(logging.getLogger('saver'))
        return self.saver

    def get_supervisor_manager(self):
        if self.supervisor_manager is None:
            self.supervisor_manager = self.supervisor_manager_class()
            self.supervisor_manager.set_logger(logging.getLogger('supervisors'))
        return self.supervisor_manager

    def add_supervisor(self, name, supervisor_class):
        self.supervisor_manager.add_supervisor(supervisor_class(name))

    def set_tagsrv_class(self, tagsrv_class):
        self.tagsrv_class = tagsrv_class

    def set_controller_class(self, controller_class):
        self.controller_class = controller_class

    def set_saver_class(self, saver_class):
        self.saver_class = saver_class
