from mechanism import Mechanism
from pylogic.channel import OutChannel
from pylogic.modbus_supervisor import ModbusDataObject
from pylogic.timer import Ton


class Siren(Mechanism, ModbusDataObject):
    _save_attrs = ('timeout',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.do_start = OutChannel(False)
        self.state = False
        self.ton = Ton()
        self.timeout = 5.0
        self.mb_cells_idx = None

    def process(self):
        if self.state:
            self.do_start.val = True
            if self.ton.process(True, self.timeout):
                self.state = False
                self.logger.info(f'{self.name}: stop')
        else:
            self.ton.process(False)
            self.do_start.val = False

    def start(self):
        if not self.state:
            self.state = True
            self.logger.info(f'{self.name}: start command')

    def stop(self):
        if self.state:
            self.state = False
            self.logger.info(f'{self.name}: stop command')

    def set_timeout(self, timeout_sec: int):
        if self.timeout != timeout_sec:
            self.timeout = timeout_sec
            self.save()
            self.logger.info(f'{self.name}: timeout set to {timeout_sec} s')

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.start()
            if cmd & 0x0002:
                self.stop()
            self.set_timeout(data[zero_addr + 1])

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = int(self.do_start.val) * (1 << 0) + int(self.state) * (1 << 1)
            return {
                self.mb_cells_idx + 0: 0,
                self.mb_cells_idx + 1: int(self.timeout),
                self.mb_cells_idx + 2: status,
            }
        else:
            return {}
