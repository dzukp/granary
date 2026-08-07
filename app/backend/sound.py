from mechanism import Mechanism
from pylogic.modbus_supervisor import ModbusDataObject


class Sound(Mechanism, ModbusDataObject):
    _save_attrs = ('enabled',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.state = False
        self.enabled = True
        self.mb_cells_idx = None

    def process(self):
        if not self.enabled:
            self.state = False

    def start(self):
        if not self.enabled:
            self.logger.warning(f'{self.name}: start ignored - disabled')
            return
        if not self.state:
            self.state = True
            self.logger.info(f'{self.name}: start command')

    def stop(self):
        if self.state:
            self.state = False
            self.logger.info(f'{self.name}: stop command')

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.logger.info(f'{self.name}: enabled')

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.state = False
            self.logger.info(f'{self.name}: disabled')

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.start()
            if cmd & 0x0002:
                self.stop()
            if cmd & 0x0020:
                self.enable()
            if cmd & 0x0040:
                self.disable()

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = int(self.state) * (1 << 0) + int(self.enabled) * (1 << 1)
            return {
                self.mb_cells_idx + 0: 0,
                self.mb_cells_idx + 1: status,
            }
        else:
            return {}
