from mechanism import Mechanism
from pylogic.channel import InChannel, OutChannel
from pylogic.modbus_supervisor import ModbusDataObject


class Releaser(Mechanism, ModbusDataObject):
    _save_attrs = ('enabled', 'control_on')

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.do_release = OutChannel(False)
        self.do_control_on = OutChannel(True)
        self.di_explosion = InChannel(False)
        self.enabled = True
        self.released = False
        self.control_on = True
        self.mb_cells_idx = None

    def process(self):
        if self.di_explosion.val and not self.released:
            self.released = True
            self.logger.warning(f'{self.name}: explosion signal - RELEASED')
        if not self.enabled:
            self.do_release.val = False
            return
        self.do_release.val = self.released
        self.do_control_on.val = self.control_on

    def is_running(self):
        return self.released

    def start(self):
        if not self.released:
            self.released = True
            self.logger.info(f'{self.name}: start - simulate explosion')

    def stop(self):
        if self.released:
            self.released = False
            self.logger.info(f'{self.name}: stop - reset')

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.save()
            self.logger.info(f'{self.name}: enabled')

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.released = False
            self.save()
            self.logger.info(f'{self.name}: disabled')

    def set_control_on(self):
        if not self.control_on:
            self.control_on = True
            self.save()
            self.logger.info(f'{self.name}: control on')

    def set_control_off(self):
        if self.control_on:
            self.control_on = False
            self.save()
            self.logger.info(f'{self.name}: control off')

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.start()
            if cmd & 0x0002:
                self.stop()
            if cmd & 0x0004:
                self.enable()
            if cmd & 0x0008:
                self.disable()
            if cmd & 0x0010:
                self.set_control_on()
            if cmd & 0x0020:
                self.set_control_off()

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(self.do_release.val) * (1 << 0)
                + int(self.di_explosion.val) * (1 << 1)
                + int(self.released) * (1 << 2)
                + int(self.enabled) * (1 << 3)
                + int(self.control_on) * (1 << 4)
            )
            return {
                self.mb_cells_idx: 0,
                self.mb_cells_idx + 1: status,
            }
        else:
            return {}
