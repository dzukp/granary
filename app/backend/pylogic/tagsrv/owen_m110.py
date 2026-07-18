from time import time

import modbus_tk
import modbus_tk.defines as cst
from pylogic.tagsrv.owen_mx210 import BaseOwenMx210


class BaseM110TcpModule(BaseOwenMx210):
    def process(self):
        try:
            self.do_request()
        except modbus_tk.modbus.ModbusError:
            self.ok = False
            self.logger.error('ModbusError')
        except TimeoutError:
            self.ok = False
            self.logger.error('socket.timeout')
            self.init()
        except Exception:
            self.ok = False
            self.logger.exception('Unexpected exception')
        else:
            self.ok = True
            self.last_ok = time()

    def do_request(self):
        raise NotImplementedError


class OwenM110DiTcpModule(BaseM110TcpModule):
    """Дискретный ввод"""

    def __init__(self, tags, ip, port=502, slave=1, timeout=0.05, **kwargs):
        super().__init__(tags, ip, port, slave, timeout)
        self.name = kwargs.get('name') or self.name
        sorted_tags = sorted(tags, key=lambda x: x.addr)
        self.quantity = 2 if sorted_tags[-1].addr - sorted_tags[0].addr > 16 else 1
        self.data_format = (
            '>I' if sorted_tags[-1].addr - sorted_tags[0].addr > 16 else '>H'
        )

    def do_request(self):
        res = self.mb.execute(
            slave=self.slave,
            function_code=cst.READ_HOLDING_REGISTERS,
            starting_address=51,
            quantity_of_x=self.quantity,
            data_format=self.data_format,
        )[0]
        # print(f'src {bin(res)[2:]}')
        res = ((res & 0x0000FFFF) << 16) + ((res & 0xFFFF0000) >> 16)
        # print(f'DiMv2010 {bin(res)[2:]}')
        self.logger.debug(
            f'data readed {bin(res)[2:].zfill(max(24, 16 * self.quantity))}',
        )
        for tag in self.tags:
            tag.value = (res & (1 << (tag.addr - 1))) != 0

    def _value_to_str(self, value):
        return str(int(value)) if value is not None else '-'


class OwenM110DoTcpModule(BaseM110TcpModule):
    """Дискретный вывод"""

    def __init__(self, tags, ip, port=502, slave=1, timeout=0.05, **kwargs):
        super().__init__(tags=tags, ip=ip, port=port, slave=slave, timeout=timeout)
        self.name = kwargs.get('name') or self.name

    def do_request(self):
        data = 0
        for tag in self.tags:
            value = bool(tag.value)
            data |= int(value) << (tag.addr - 1)
        self.mb.execute(
            slave=self.slave,
            function_code=cst.WRITE_MULTIPLE_REGISTERS,
            starting_address=50,
            quantity_of_x=1,
            output_value=(data,),
            data_format='>H',
        )
        self.logger.debug(
            f'Write data request ok. data = {bin(data)[2:].zfill(16)}',
        )

    def _value_to_str(self, value):
        return str(int(value)) if value is not None else '-'
