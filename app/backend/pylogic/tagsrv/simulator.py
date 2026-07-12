from .module_dispatcher import ModuleDispatcher

import logging


class SimulatorModule(object):
    
    def __init__(self, real_tags, sim_channels):
        self.real_in_tags = real_tags['in']
        self.real_out_tags = real_tags['out']
        #self.sim_channels = dict((ch.name, ch)for ch in sim_channels)
        self.sim_channels = {} 
        for ch in sim_channels:
            if ch.name not in self.sim_channels:
                self.sim_channels[ch.name] = []
            self.sim_channels[ch.name].append(ch)
        self.in_tags = {}
        for name, tag in self.real_in_tags.items():
            if name in self.sim_channels:
                self.in_tags[name] = (tag, self.sim_channels[name][0])
        self.out_tags = {}
        for name, tag in self.real_out_tags.items():
            if name in self.sim_channels:
                self.out_tags[name] = [(tag, ch) for ch in self.sim_channels[name]]
    
    def process(self):
        for rtag, stag in self.in_tags.values():
            rtag.value = stag.val
        for otags in self.out_tags.values():
            for otag in otags:
                #otag[1].val = otag[0].value
                otag[1].set_value(otag[0].value)
    
    
class SimulatorDispatcher(ModuleDispatcher):
    
    def __init__(self, tags, sim_channels):
        super(SimulatorDispatcher, self).__init__([SimulatorModule(tags, sim_channels),], 0.1)
        self.set_logger(logging.getLogger('tag_srv.simulator'))
    
    def process(self):
        for m in self.modules:
            m.process()
