from exceptions import LogicException
from mechanism import Mechanism
from pylogic.channel import InChannel, OutChannel
from pylogic.modbus_supervisor import ModbusDataObject
from pylogic.timer import Ton


class Engine(Mechanism, ModbusDataObject):
    # Состояния привода
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3
    FAULT = 4
    NOT_READY = 5

    _save_attrs = ('timeout', 'disabled_di')

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.do_start = OutChannel(False)
        self.di_started = InChannel(False)
        self.di_ready = InChannel(False)
        self.disabled_di = False
        self.enabled = True
        self.state = self.STOPPED
        self.ton = Ton()
        self.timeout = 5.0
        self.mb_cells_idx = None

    def process(self):
        # Если нет сигнала готовности и DI не игнорируются - переходим в NOT_READY
        if not self.disabled_di and not self.di_ready.val:
            if self.state not in (self.FAULT, self.NOT_READY):
                self._set_state(self.NOT_READY)
                self.logger.warning(f'{self.name}: not ready')

        elif self.state == self.NOT_READY:
            # Готовность восстановилась - возвращаемся в STOPPED
            self._set_state(self.STOPPED)
            self.logger.info(f'{self.name}: ready, state -> STOPPED')

        if self.state == self.STOPPED:
            self.do_start.val = False
            self.ton.process(False, self.timeout)

        elif self.state == self.STARTING:
            self.do_start.val = True
            if not self.check_next_mechanisms():
                self._set_state(self.STOPPING)
                self.logger.warning(
                    f'{self.name}: next mechanism not running -> STOPPING',
                )
            else:
                started = self.di_started.val if not self.disabled_di else True
                if self.ton.process(not started, self.timeout):
                    # Таймаут истёк, а привод не запустился - авария
                    if not started:
                        self._set_state(self.FAULT)
                        self.logger.error(
                            f'{self.name}: start timeout -> FAULT',
                        )
                elif started:
                    self._set_state(self.RUNNING)
                    self.logger.info(f'{self.name}: running')

        elif self.state == self.RUNNING:
            self.do_start.val = True
            self.ton.process(False, self.timeout)
            # Пропадание di_started во время работы - авария
            if not self.disabled_di and not self.di_started.val:
                self._set_state(self.FAULT)
                self.logger.error(f'{self.name}: di_started lost -> FAULT')
            elif not self.check_next_mechanisms():
                self._set_state(self.STOPPING)
                self.logger.warning(
                    f'{self.name}: next mechanism not running -> STOPPING',
                )

        elif self.state == self.STOPPING:
            self.do_start.val = False
            started = self.di_started.val if not self.disabled_di else False
            if self.ton.process(started, self.timeout):
                # Таймаут истёк, а привод не остановился - авария
                if started:
                    self._set_state(self.FAULT)
                    self.logger.error(f'{self.name}: stop timeout -> FAULT')
            elif not started:
                self._set_state(self.STOPPED)
                self.logger.info(f'{self.name}: stopped')

        elif self.state == self.FAULT:
            self.do_start.val = False
            self.ton.process(False, self.timeout)

        elif self.state == self.NOT_READY:
            self.do_start.val = False
            self.ton.process(False, self.timeout)

        else:
            raise LogicException(f'{self.name}: invalid state: {self.state}')

    def is_running(self):
        return self.state in (self.STARTING, self.RUNNING)

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.logger.info(f'{self.name}: enabled')

    def disable(self):
        if self.enabled:
            self.enabled = False
            self._set_state(self.STOPPING)
            self.logger.info(f'{self.name}: disabled -> STOPPING')

    def start(self):
        if not self.enabled:
            self.logger.warning(f'{self.name}: start ignored - disabled')
            return
        if self.state == self.FAULT:
            self.logger.warning(f'{self.name}: start command ignored - FAULT')
            return
        if not self.disabled_di and not self.di_ready.val:
            self.logger.warning(
                f'{self.name}: start command ignored - NOT_READY',
            )
            return
        if self.state != self.STARTING:
            self._set_state(self.STARTING)
            self.logger.info(f'{self.name}: start command')

    def stop(self):
        if self.state == self.FAULT:
            self.logger.warning(f'{self.name}: stop command ignored - FAULT')
            return
        if self.state != self.STOPPING:
            self._set_state(self.STOPPING)
            self.logger.info(f'{self.name}: stop command')

    def reset(self):
        if self.state == self.FAULT:
            self._set_state(self.STOPPED)
            self.logger.info(f'{self.name}: reset -> STOPPED')

    def disable_di(self):
        if not self.disabled_di:
            self.disabled_di = True
            self.save()
            self.logger.info(f'{self.name}: disable DI')

    def enable_di(self):
        if self.disabled_di:
            self.disabled_di = False
            self.save()
            self.logger.info(f'{self.name}: enable DI')

    def set_timeout(self, timeout_sec: int):
        if self.timeout != timeout_sec:
            self.timeout = timeout_sec
            self.save()
            self.logger.info(f'{self.name}: timeout set to {timeout_sec} s')

    def _set_state(self, state: int):
        if self.state != state:
            self.state = state
            self.ton.reset()

    def mb_input(self, start_addr, data):
        if self.mb_cells_idx is not None:
            zero_addr = self.mb_cells_idx - start_addr
            cmd = data[zero_addr]
            if cmd & 0x0001:
                self.start()
            if cmd & 0x0002:
                self.stop()
            if cmd & 0x0004:
                self.disable_di()
            if cmd & 0x0008:
                self.enable_di()
            if cmd & 0x0010:
                self.reset()
            if cmd & 0x0020:
                self.enable()
            if cmd & 0x0040:
                self.disable()
            self.set_timeout(data[zero_addr + 1])

    def mb_output(self, start_addr):
        if self.mb_cells_idx is not None:
            status = (
                int(self.di_started.val) * (1 << 0)
                + int(self.di_ready.val) * (1 << 1)
                + int(self.do_start.val) * (1 << 2)
                + int(self.disabled_di) * (1 << 3)
                + int(self.enabled) * (1 << 4)
            )
            return {
                self.mb_cells_idx + 0: 0,
                self.mb_cells_idx + 1: int(self.timeout),
                self.mb_cells_idx + 2: status,
                self.mb_cells_idx + 3: self.state,
            }
        else:
            return {}
