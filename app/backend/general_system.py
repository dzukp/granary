from engine import Engine
from mechanism import MechManager
from pylogic.channel import InChannel
from pylogic.io_object import IoObject
from pylogic.modbus_supervisor import ModbusDataObject
from silo import Silo
from valve import Valve


class GeneralSystem(IoObject, MechManager, ModbusDataObject):
    _save_attrs = (
        'silos_ready_enabled',
        'socket_1_enabled',
        'socket_2_enabled',
        'socket_3_enabled',
    )

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

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.silos_ready_enabled = True
            if cmd & 0x0002:
                self.silos_ready_enabled = False

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(self.di_silos_ready.val) * (1 << 0)
                + int(self.silos_ready_enabled) * (1 << 0)
                + int(self.di_socket_1.val) * (1 << 2)
                + int(self.socket_1_enabled) * (1 << 3)
                + int(self.di_socket_2.val) * (1 << 4)
                + int(self.socket_2_enabled) * (1 << 5)
                + int(self.di_socket_3.val) * (1 << 6)
                + int(self.socket_3_enabled) * (1 << 7)
            )
            return {
                self.mb_cells_idx: 0,
                self.mb_cells_idx + 1: status,
            }
        else:
            return {}
