from time import time, sleep
import logging

from .logged_object import LoggedObject
from .channel import InChannel, OutChannel, InOutChannel
from .timer import default_periodic_clock


class Controller(LoggedObject):

    def __init__(self):
        super().__init__('Controller')
        self.tag_server = None
        self.top_object = None
        self.sim_object = None
        self.saver = None
        self.supervisor_manager = None
        self.cycle_time = 0.05

    def set_tag_server(self, tag_server):
        self.tag_server = tag_server

    def set_top_object(self, top_object):
        self.top_object = top_object

    def set_sim_object(self, sim_object):
        self.sim_object = sim_object

    def set_saver(self, saver):
        self.saver = saver

    def set_supervisor_manager(self, supervisor_manager):
        self.supervisor_manager = supervisor_manager

    def init(self):
        self.top_object.set_saver(self.saver)
        self.top_object.load_all()
        self.top_object.init_all()
        if self.sim_object:
            self.sim_object.init_all()
        self.test_channel_attaching()
        self.supervisor_manager.set_top_object(self.top_object)
        self.supervisor_manager.set_tag_srv(self.tag_server)
        self.supervisor_manager.init()

    def test_channel_attaching(self):
        in_tag_atached_channel_names = []
        for tag in self.tag_server.in_tags:
            in_tag_atached_channel_names += [ch.name for ch in tag.channels]
        out_tag_atached_channel_names = []
        for tag in self.tag_server.out_tags:
            if tag.channel is not None:
                out_tag_atached_channel_names.append(tag.channel.name)
        for channel in self.top_object.get_all_channels():
            if channel.name:
                if isinstance(channel, (InChannel, InOutChannel)):
                    count = in_tag_atached_channel_names.count(channel.name)
                    if count == 0:
                        self.logger.warning(f'{type(channel).__name__} `{channel.name} has no attached tag')
                    elif count > 1:
                        self.logger.warning(f'{type(channel).__name__} `{channel.name}` has more 1 attached tag')
                if isinstance(channel, (OutChannel, InOutChannel)):
                    if channel.name not in out_tag_atached_channel_names:
                        self.logger.warning(f'{type(channel).__name__} `{channel.name}` has no attached tag')
            else:
                self.logger.warning('Channel has no name')

    def process(self):
        self.supervisor_manager.receive_data()
        self.tag_server.read_all()
        self.top_object.process_all()
        if self.sim_object:
            self.sim_object.process_all()
        self.tag_server.write_all()
        self.tag_server.process()
        self.supervisor_manager.send_data()

    def start_loop(self):
        self.tag_server.start()
        while True:
            t0 = time()
            default_periodic_clock.update()
            self.process()
            dt = time() - t0
            sleep_time = max(0.0, self.cycle_time - dt)
            self.logger.debug(f'End circle, time: {dt}s')
            sleep(sleep_time)
