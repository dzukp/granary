from audio_player import AudioPlayer
from mechanism import Mechanism
from pylogic.modbus_supervisor import ModbusDataObject


class Sound(Mechanism, ModbusDataObject):
    _save_attrs = ('enabled',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.state = False
        self.manual_start = False
        self.mb_cells_idx = None
        self.acknowledged_errors = set()
        self.current_errors = set()
        self.file_path = None
        self._player = None

    def process(self):
        self.acknowledged_errors &= self.current_errors
        if (self.current_errors - self.acknowledged_errors) or self.manual_start:
            self._start_sound()
        else:
            self._stop_sound()

    def start(self):
        if not self.manual_start:
            self.manual_start = True
            self.logger.info(f'{self.name}: start command')

    def stop(self):
        if self.manual_start:
            self.manual_start = False
            self.logger.info(f'{self.name}: stop command')

    def acknowledge(self):
        self.acknowledged_errors = self.current_errors.copy()
        self.logger.info(f'{self.name}: acknowledged')

    def add_error(self, error):
        if error not in self.current_errors:
            self.current_errors.add(error)
            self.logger.info(f'{self.name}: error added: {error}')

    def del_error(self, error):
        if error in self.current_errors:
            self.current_errors.remove(error)
            self.logger.info(f'{self.name}: error removed: {error}')

    def set_current_errors(self, errors):
        if self.current_errors != errors:
            self.current_errors = set(errors)
            self.logger.info(f'{self.name}: errors set: {sorted(self.current_errors)}')

    def _start_sound(self):
        if not self.file_path:
            self.logger.warning(f'{self.name}: no audio file set')
            return
        if self._player is None:
            self._player = AudioPlayer(self.logger, self.file_path)
        self._player.play()
        self.state = True

    def _stop_sound(self):
        if self._player is not None:
            self._player.stop()
        self.state = False

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.start()
            if cmd & 0x0002:
                self.stop()
            if cmd & 0x0004:
                self.acknowledge()

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(bool(self.current_errors)) * (1 << 0)
                | int(self.manual_start) * (1 << 1)
                | int(self.state) * (1 << 2)
            )
            return {
                self.mb_cells_idx + 0: 0,
                self.mb_cells_idx + 1: status,
            }
        else:
            return {}
