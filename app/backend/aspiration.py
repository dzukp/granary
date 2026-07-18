from mechanism import MechManager
from pylogic.io_object import IoObject
from pylogic.modbus_supervisor import ModbusDataObject


class Aspiration(IoObject, MechManager, ModbusDataObject):
    _save_attrs = ('aspiration_enabled',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.mb_cells_idx = None
        self.aspiration_enabled = False
        self.sluice_16_3 = None
        self.fan_15_3 = None

    def is_running(self):
        return self.fan_15_3.is_running() and self.sluice_16_3.is_running()

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            pass

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = 0
            return {
                self.mb_cells_idx - start_addr + 0: 2222,
                self.mb_cells_idx - start_addr + 1: status,
            }
        return {}
