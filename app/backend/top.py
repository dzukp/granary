import time

from mechanism import Mechanism, MechManager
from pylogic.channel import InChannel, OutChannel, ModuleStateChannel
from pylogic.io_object import IoObject
from pylogic.modbus_supervisor import ModbusDataObject
from pylogic.timer import Ton


class Top(IoObject, MechManager, ModbusDataObject):
    _save_attrs = ('explosion_control_enabled',)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.di_explosion = InChannel(False)
        self.do_releaser = OutChannel(False)
        self.human_name = ''
        self.explosion_control_enabled = False
        self.aspiration = None
        self.general_system = None
        self.sound = None
        self.counter = 0
        self.counter_ton = Ton()
        self.mb_cells_idx = None
        self.modules: list[ModuleStateChannel] = []
        self.last_module_states: list[bool | None] = []
        self.module_names = {}
        for i in range(1, 19):
            variable = f'm_di_{i:02}'
            self.__dict__[variable] = ModuleStateChannel()
            self.modules.append(self.__dict__[variable])
            self.module_names[self.__dict__[variable]] = f'А{i}'
        for i in range(21, 31):
            variable = f'm_do_{i:02}'
            self.__dict__[variable] = ModuleStateChannel()
            self.modules.append(self.__dict__[variable])
            self.module_names[self.__dict__[variable]] = f'А{i}'
        for i in range(31, 33):
            variable = f'm_ai_{i:02}'
            self.__dict__[variable] = ModuleStateChannel()
            self.modules.append(self.__dict__[variable])
            self.module_names[self.__dict__[variable]] = f'А{i}'
        self.last_module_states = [None for _ in self.modules]
        self.start_time = time.time()

    def init(self):
        self.info('Старт')

    def process_all(self):
        if time.time() - self.start_time > 3.0:
            super().process_all()

    def process(self):
        self.check_module_states()
        if self.explosion_control_enabled:
            if self.di_explosion.val:
                if not self.do_releaser.val:
                    self.do_releaser.val = True
                    self.logger.warning('Сработал расцепитель')
                    self.info('Сработал расцепитель')
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

        if self.sound is not None:
            self.sound.set_current_errors(self._collect_faults(self))

    def check_module_states(self):
        for module, last in zip(self.modules, self.last_module_states):
            if module.online != last:
                idx = self.modules.index(module)
                if self.last_module_states[idx] is not None:
                    if not module.online:
                        self.error(
                            f'Модуль ввода-вывода {self.module_names[module]} не отвечает'
                        )
                    else:
                        self.info(
                            f'Модуль ввода-вывода {self.module_names[module]} на связи'
                        )
                    self.logger.warning(
                        f'{self.module_names[module]}: {"online" if module.online else "offline"}'
                    )
                self.last_module_states[idx] = module.online

    def _collect_faults(self, obj):
        faults = set()
        for child in obj.children:
            if isinstance(child, Mechanism) and child.is_fault():
                faults.add(child.full_name)
            faults |= self._collect_faults(child)
        return faults

    def mb_cells(self):
        return [0, self.mb_cells_idx + len(self.mb_output(self.mb_cells_idx))]

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            pass

    def _pack_word(self, modules):
        """Состояния модулей: каждый модуль = бит (1 = не отвечает)."""
        word = 0
        for j, module in enumerate(modules):
            if module.online:
                word |= 1 << j
        return word

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(self.explosion_control_enabled) * (1 << 0)
                + int(self.di_explosion.val) * (1 << 1)
                + 0
            )
            modules = self.modules
            modules_word_1 = self._pack_word(modules[0:16])
            modules_word_2 = self._pack_word(modules[16:32])
            out = {
                self.mb_cells_idx - start_addr + 0: 1111,
                self.mb_cells_idx - start_addr + 1: 2222,
                self.mb_cells_idx - start_addr + 2: 3333,
                self.mb_cells_idx - start_addr + 3: self.counter,
                self.mb_cells_idx - start_addr + 4: status,
                self.mb_cells_idx - start_addr + 5: modules_word_1,
                self.mb_cells_idx - start_addr + 6: modules_word_2,
            }
            return out
        return {}
