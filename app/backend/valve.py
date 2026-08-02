from exceptions import LogicException
from mechanism import Mechanism
from pylogic.channel import InChannel, OutChannel
from pylogic.modbus_supervisor import ModbusDataObject
from pylogic.timer import Ton


class Valve(Mechanism, ModbusDataObject):
    # Состояния задвижки
    CLOSED = 0
    OPENING = 1
    OPENED = 2
    CLOSING = 3
    FAULT = 4
    NOT_READY = 5
    UNDEFINED = 6

    _save_attrs = ('timeout', 'disabled_di')

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.do_open = OutChannel(False)
        self.do_close = OutChannel(False)
        self.di_ready = InChannel(False)
        self.di_opened = InChannel(False)
        self.di_closed = InChannel(False)
        self.disabled_di = False
        self.enabled = True
        self.state = self.UNDEFINED
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
            # Готовность восстановилась - переходим в UNDEFINED
            self._set_state(self.UNDEFINED)
            self.logger.info(f'{self.name}: ready, state -> UNDEFINED')

        if self.state == self.CLOSED:
            self.do_open.val = False
            self.do_close.val = False
            self.ton.process(False, self.timeout)

        elif self.state == self.OPENING:
            self.do_open.val = True
            self.do_close.val = False
            if not self.check_next_mechanisms():
                self._set_state(self.CLOSING)
                self.logger.warning(
                    f'{self.name}: next mechanism not running -> CLOSING',
                )
            else:
                opened = self.di_opened.val if not self.disabled_di else False
                if self.ton.process(not opened, self.timeout):
                    if self.disabled_di:
                        opened = True
                    # Таймаут истёк, а задвижка не открылась - авария
                    elif not opened:
                        self._set_state(self.FAULT)
                        self.logger.error(
                            f'{self.name}: open timeout -> FAULT',
                        )
                if opened:
                    self._set_state(self.OPENED)
                    self.logger.info(f'{self.name}: opened')

        elif self.state == self.OPENED:
            self.do_open.val = False
            self.do_close.val = False
            self.ton.process(False, self.timeout)
            if not self.check_next_mechanisms():
                self._set_state(self.CLOSING)
                self.logger.warning(
                    f'{self.name}: next mechanism not running -> CLOSING',
                )

        elif self.state == self.CLOSING:
            self.do_open.val = False
            self.do_close.val = True
            closed = self.di_closed.val if not self.disabled_di else False
            if self.ton.process(not closed, self.timeout):
                if self.disabled_di:
                    closed = True
                # Таймаут истёк, а задвижка не закрылась - авария
                elif not closed:
                    self._set_state(self.FAULT)
                    self.logger.error(f'{self.name}: close timeout -> FAULT')
            if closed:
                self._set_state(self.CLOSED)
                self.logger.info(f'{self.name}: closed')

        elif self.state == self.FAULT:
            self.do_open.val = False
            self.do_close.val = False
            self.ton.process(False, self.timeout)

        elif self.state == self.NOT_READY:
            self.do_open.val = False
            self.do_close.val = False
            self.ton.process(False, self.timeout)

        elif self.state == self.UNDEFINED:
            self.do_open.val = False
            self.do_close.val = False
            self.ton.process(False, self.timeout)
            if not self.disabled_di:
                if self.di_closed.val:
                    self._set_state(self.CLOSED)
                    self.logger.info(
                        f'{self.name}: undefined -> CLOSED (di_closed)',
                    )
                elif self.di_opened.val:
                    self._set_state(self.OPENED)
                    self.logger.info(
                        f'{self.name}: undefined -> OPENED (di_opened)',
                    )
        else:
            raise LogicException(f'{self.name}: invalid state: {self.state}')

    def is_running(self):
        if not self.enabled:
            return False
        return self.state in (self.OPENING, self.CLOSING)

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.logger.info(f'{self.name}: enabled')

    def disable(self):
        if self.enabled:
            self.enabled = False
            self._set_state(self.CLOSING)
            self.logger.info(f'{self.name}: disabled -> CLOSING')

    def open(self):
        if not self.enabled:
            self.logger.warning(f'{self.name}: open ignored - disabled')
            return
        if self.state in (self.FAULT,):
            self.logger.warning(
                f'{self.name}: open command ignored - {self.state}',
            )
            return
        if not self.disabled_di and not self.di_ready.val:
            self.logger.warning(
                f'{self.name}: open command ignored - NOT_READY',
            )
            return
        if self.state != self.OPENING:
            self._set_state(self.OPENING)
            self.logger.info(f'{self.name}: open command')

    def close(self):
        if not self.enabled:
            self.logger.warning(f'{self.name}: close ignored - disabled')
            return
        if self.state in (self.FAULT,):
            self.logger.warning(
                f'{self.name}: close command ignored - {self.state}',
            )
            return
        if not self.disabled_di and not self.di_ready.val:
            self.logger.warning(
                f'{self.name}: close command ignored - NOT_READY',
            )
            return
        if self.state != self.CLOSING:
            self._set_state(self.CLOSING)
            self.logger.info(f'{self.name}: close command')

    def reset(self):
        if self.state == self.FAULT:
            self._set_state(self.UNDEFINED)
            self.logger.info(f'{self.name}: reset -> UNDEFINED')

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
                self.open()
            if cmd & 0x0002:
                self.close()
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
                int(self.di_opened.val) * (1 << 0)
                + int(self.di_closed.val) * (1 << 1)
                + int(self.di_ready.val) * (1 << 2)
                + int(self.do_open.val) * (1 << 3)
                + int(self.do_close.val) * (1 << 4)
                + int(self.disabled_di) * (1 << 5)
                + int(self.enabled) * (1 << 6)
                + int(self.state == self.OPENED) * (1 << 7)
            )
            return {
                self.mb_cells_idx - start_addr + 0: 0,
                self.mb_cells_idx - start_addr + 1: int(self.timeout),
                self.mb_cells_idx - start_addr + 2: status,
                self.mb_cells_idx - start_addr + 3: self.state,
            }
        else:
            return {}
