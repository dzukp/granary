from mechanism import Mechanism
from pylogic.io_object import IoObject
from pylogic.channel import InChannel
from pylogic.modbus_supervisor import ModbusDataObject


class Silo(Mechanism, ModbusDataObject):
    _save_attrs = ('disabled_di',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.di_top_level    = InChannel(False)
        self.di_bottom_level = InChannel(False)
        self.disabled_di     = False
        self.enabled         = True
        self.ready           = False
        self.enabled         = True
        self.mb_cells_idx    = None

    def process(self):
        pass

    def is_running(self):
        if not self.enabled:
            return False
        if self.disabled_di:
            return True
        if not self.ready:
            return False
        if self.di_top_level.val:
            return False
        return True

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.logger.info(f'{self.name}: enabled')

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.logger.info(f'{self.name}: disabled')

    def set_ready(self, value: bool):
        if self.ready != value:
            self.ready = value
            self.logger.info(f'{self.name}: ready -> {value}')

    def disable_di(self):
        if not self.disabled_di:
            self.disabled_di = True
            self.logger.info(f'{self.name}: disable DI')

    def enable_di(self):
        if self.disabled_di:
            self.disabled_di = False
            self.logger.info(f'{self.name}: enable DI')

    def mb_cells(self):
        return self.mb_output(0).keys()

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.disable_di()
            if cmd & 0x0002:
                self.enable_di()
            if cmd & 0x0004:
                self.enable()
            if cmd & 0x0008:
                self.disable()

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(self.ready)               * (1 << 0) +
                int(self.di_top_level.val)    * (1 << 1) +
                int(self.di_bottom_level.val) * (1 << 2) +
                int(self.disabled_di)         * (1 << 3) +
                int(self.enabled)             * (1 << 4) +
                int(self.is_running())        * (1 << 5)
            )
            return {
                self.mb_cells_idx:     0,      # 0-я ячейка — команды от СКАДА, в output передаём 0
                self.mb_cells_idx + 1: status,
            }
        else:
            return {}
