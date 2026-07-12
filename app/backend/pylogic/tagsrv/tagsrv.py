import logging

from .simulator import SimulatorDispatcher
from .tagsrv_logger import logger


class InTag:
    def __init__(self, addr, fltr=None):
        self.filter = fltr
        self.channels = []
        self.value = None
        self.addr = addr

        
class OutTag:
    def __init__(self, addr, fltr=None):
        self.filter = fltr
        self.channel = None
        self.value = None
        self.addr = addr
        

class TagSrv(object):
    
    def __init__(self):
        self.in_tags = []
        self.out_tags = []
        self.channels = []
        self.dispatchers = {}
        self.logger = logger  # logging.getLogger('tag_srv')
        self.sim_dispatchers = None
    
    def init(self, setting, channels, sim_channels=()):
        self.in_tags = list(setting['tags']['in'].values()) if 'in' in setting['tags'] else []
        self.out_tags = list(setting['tags']['out'].values()) if 'out' in setting['tags'] else []
        self.dispatchers = setting['dispatchers']
        for name, disp in self.dispatchers.items():
            disp.set_logger(self.logger.getChild(name))
        self.channels = channels
        for ch in self.channels:
            if 'in' in setting['tags'] and ch.name in setting['tags']['in']:
                setting['tags']['in'][ch.name].channels.append(ch)
            elif 'out' in setting['tags'] and ch.name in setting['tags']['out']:
                setting['tags']['out'][ch.name].channel = ch
        if sim_channels:
            self.sim_dispatchers = {
                'Simulator': SimulatorDispatcher(setting['tags'], sim_channels)
            }
    
    def start(self):
        self.logger.info('Start dispatchers')
        if self.sim_dispatchers:
            dispatchers = self.sim_dispatchers
        else:
            dispatchers = self.dispatchers
        for name, d in dispatchers.items():
            d.setName(name)
            d.start()
    
    def process(self):
        pass
    
    def read_all(self):
        for t in self.in_tags:
            if t.value is not None:
                for ch in t.channels:
                    ch.set_value(t.value)
        # self.logger.debug('read all %s' % [[f'{ch.name}={t.value}' for ch in t.channels] for t in self.in_tags if t.channels])
    
    def write_all(self):
        for t in self.out_tags:
            if t.channel:
                t.value = t.channel.get_value()
            else:
                t.value = 0
        # self.logger.debug('write all %s' % [f'{t.channel.name}={t.value}' for t in self.out_tags if t.channel])
