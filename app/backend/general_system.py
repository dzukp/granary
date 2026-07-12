from engine import Engine
from mechanism import Mechanism, MechManager
from pylogic.channel import InChannel
from pylogic.io_object import IoObject
from pylogic.modbus_supervisor import ModbusDataObject
from silo import Silo
from valve import Valve


class GeneralSystem(IoObject, MechManager, ModbusDataObject):
    _save_attrs = ('silos_ready_enabled', 'socket_1_enabled', 'socket_2_enabled', 'socket_3_enabled')

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.mb_cells_idx = None
        self.di_silos_ready = InChannel(False)
        self.di_socket_1 = InChannel(False)
        self.di_socket_2 = InChannel(False)
        self.di_socket_3 = InChannel(False)
        self.silos_ready_enabled = False
        self.socket_1_enabled = False
        self.socket_2_enabled = False
        self.socket_3_enabled = False
        self.silos: list[Silo] = []
        self.valves: list[Valve] = []
        self.engines: list[Engine] = []

    def init(self):
        self.silos = [mech for mech in self.children if isinstance(mech, Silo)]
        self.valves = [mech for mech in self.children if isinstance(mech, Valve)]
        self.engines = [mech for mech in self.children if isinstance(mech, Engine)]

    def process(self):
        for silo in self.silos:
            silo.set_ready(not self.silos_ready_enabled or self.di_silos_ready.val)
