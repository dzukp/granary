from mechanism import MechManager
from pylogic.channel import InChannel, OutChannel
from pylogic.io_object import IoObject
from pylogic.modbus_supervisor import ModbusDataObject
from pylogic.timer import Ton


class Top(IoObject, MechManager, ModbusDataObject):
    _save_attrs = ('explosion_control_enabled',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.di_explosion = InChannel(False)
        self.do_releaser = OutChannel(False)
        self.explosion_control_enabled = False
        self.aspiration = None
        self.general_system = None
        self.counter = 0
        self.counter_ton = Ton()
        self.mb_cells_idx = None

    def process(self):
        if self.explosion_control_enabled:
            if self.di_explosion.val:
                if not self.do_releaser.val:
                    self.do_releaser.val = True
                    self.logger.warning('Сработал расцепитель')
            self.do_releaser.val = self.di_explosion.val
        else:
            self.do_releaser.val = False

        if self.aspiration.is_running():
            self.general_system.enable()
        else:
            self.general_system.disable()

        if self.counter_ton.process(True, 0.5):
            self.counter = (self.counter + 1) % 2**16
            self.counter_ton.process(False)

    def mb_cells(self):
        return [0, self.mb_cells_idx + len(self.mb_output(self.mb_cells_idx))]

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            pass

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(self.explosion_control_enabled) * (1 << 0)
                + int(self.di_explosion.val) * (1 << 1)
                + 0
            )
            return {
                self.mb_cells_idx - start_addr + 0: 1111,
                self.mb_cells_idx - start_addr + 1: 2222,
                self.mb_cells_idx - start_addr + 2: 3333,
                self.mb_cells_idx - start_addr + 3: self.counter,
                self.mb_cells_idx - start_addr + 4: status,
            }
        return {}
