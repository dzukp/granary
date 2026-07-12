import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp, hooks
import struct
import socket
from time import time, sleep

from .tagsrv_logger import logger
from .tagsrv import InTag, OutTag
from .module import BaseModule


class BaseOwenMx210(BaseModule):

    def __init__(self, tags, ip, port=502, slave=1, timeout=0.05):
        super(BaseOwenMx210, self).__init__(name=f'{ip}')
        self.ip = ip
        self.port = port
        self.slave = slave
        self.timeout = timeout
        self.tags = tags
        self.logger = logger.getChild(f'{type(self).__name__}_{ip.replace(".","")}_{port}')
        self.mb = None
        self.init()

    def init(self):
        self.mb = modbus_tcp.TcpMaster(host=self.ip, port=self.port)
        self.mb.set_timeout(min(0.02, self.timeout))

    def set_logger(self, logger):
        self.logger = logger

    def loop(self):
        while True:
            t0 = time()
            try:
                self.process()
            except modbus_tk.modbus.ModbusError:
                self.ok = False
                self.logger.error('ModbusError')
            except socket.timeout:
                self.ok = False
                self.logger.error('socket.timeout')
                self.init()
            except Exception:
                self.ok = False
                self.logger.exception('Unexpected exception')
            else:
                self.ok = True
                self.last_ok = time()
            finally:
                sleep_time = max(0.0, t0 + self.timeout - time())
                sleep(sleep_time)

    def process(self):
        raise Exception('Need implement')


class OwenDiMv210(BaseOwenMx210):
    """ Discrete input module МВ210 """

    def __init__(self, tags, ip, port=502, slave=1, timeout=0.05):
        super().__init__(tags, ip, port, slave, timeout)
        sorted_tags = sorted(tags, key=lambda x: x.addr)
        self.quantity = 2 if sorted_tags[-1].addr - sorted_tags[0].addr > 16 else 1
        self.data_format = '>I' if sorted_tags[-1].addr - sorted_tags[0].addr > 16 else '>H'

    def process(self):
        res = self.mb.execute(slave=self.slave, function_code=cst.READ_HOLDING_REGISTERS, starting_address=51,
                              quantity_of_x=self.quantity, data_format=self.data_format)[0]
        # print(f'src {bin(res)[2:]}')
        res = ((res & 0x0000FFFF) << 16) + ((res & 0xFFFF0000) >> 16)
        # print(f'DiMv2010 {bin(res)[2:]}')
        self.logger.debug(f'data readed {bin(res)[2:].zfill(max(24, 16 * self.quantity))}')
        for tag in self.tags:
            tag.value = (res & (1 << (tag.addr - 1))) != 0

    def _value_to_str(self, value):
        return str(int(value)) if value is not None else '-'


class OwenDoMu210_401(BaseOwenMx210):
    """ Discrete output module МУ210-401 и МУ210-402 """

    def process(self):
        data = 0
        for tag in self.tags:
            value = bool(tag.value)
            data |= (int(value) << (tag.addr - 1))
        res = self.mb.execute(slave=self.slave, function_code=cst.WRITE_MULTIPLE_REGISTERS, starting_address=470,
                        quantity_of_x=1, output_value=(data,), data_format='>H')
        self.logger.debug(f'Write data request ok. data = {bin(data)[2:].zfill(16)}')

    def _value_to_str(self, value):
        return str(int(value)) if value is not None else '-'


class OwenDoMu210_403(BaseOwenMx210):
    """ Discrete output module МУ210-403 и МУ210-410"""

    def process(self):
        data = 0
        for tag in self.tags:
            value = bool(tag.value)
            data |= (int(value) << (tag.addr - 1))
        write_data = (data & 0xFFFF), (data & 0xFFFF0000) >> 16
        res = self.mb.execute(slave=self.slave, function_code=cst.WRITE_MULTIPLE_REGISTERS, starting_address=470,
                        quantity_of_x=2, output_value=write_data, data_format='>HH')
        self.logger.debug(f'Write data request ok. data = {bin(data)[2:].zfill(16)}')

    def _value_to_str(self, value):
        return str(int(value)) if value is not None else '-'


class OwenDiDoMk210(BaseOwenMx210):
    """ Discrete input/output module МК210 """

    def __init__(self, tags, ip, port=502, slave=1, timeout=0.05):
        super().__init__(tags, ip, port, slave, timeout)
        sorted_tags = sorted(tags, key=lambda x: x.addr)
        self.input_tags = [tag for tag in self.tags if isinstance(tag, InTag)]
        self.output_tags = [tag for tag in self.tags if isinstance(tag, OutTag)]

    def process(self):
        # Read input data
        res = self.mb.execute(slave=self.slave, function_code=cst.READ_HOLDING_REGISTERS, starting_address=51,
                              quantity_of_x=1, data_format='>H')[0]
        self.logger.debug(f'data readed {bin(res)[2:].zfill(16)}')
        for tag in self.input_tags:
            tag.value = (res & (1 << (tag.addr - 1))) != 0
            self.logger.debug(f'DiMv210[{self.ip}]{tag.addr} = {tag.value}')
        # Write output data
        data = 0
        for tag in self.output_tags:
            value = bool(tag.value)
            data |= (int(value) << (tag.addr - 1))
        res = self.mb.execute(slave=self.slave, function_code=cst.WRITE_MULTIPLE_REGISTERS, starting_address=470,
                        quantity_of_x=1, output_value=(data,), data_format='>H')
        self.logger.debug(f'Write data request ok. data = {bin(data)[2:].zfill(8)}')

    def _value_to_str(self, value):
        return str(int(value)) if value is not None else '-'


class OwenAiMv210(BaseOwenMx210):
    """ Analog input module МВ210 """

    def process(self):
        res = self.mb.execute(slave=self.slave, function_code=cst.READ_HOLDING_REGISTERS, starting_address=4000,
                              quantity_of_x=24, data_format='>' + 'H' * 24)
        self.logger.debug(f'data readed {[x for x in res]}')
        f_data = [struct.unpack('>f', struct.pack('>HH', res[i * 3 + 1], res[i * 3]))[0] for i in range(0, 8)]
        for tag in self.tags:
            tag.value = tag.filter.apply(f_data[tag.addr - 1]) if tag.filter else f_data[tag.addr - 1]
        self.logger.debug(f'values readed {[tag.value for tag in self.tags]}')


class OwenAoMu210(BaseOwenMx210):
    """ Analog output module МУ210 """

    def process(self):
        data = [0,] * 8
        for tag in self.tags:
            data[tag.addr - 1] = tag.filter.apply(tag.value) if tag.filter else tag.value
        self.mb.execute(slave=self.slave, function_code=cst.WRITE_MULTIPLE_REGISTERS, starting_address=3000,
                        quantity_of_x=8, output_value=data, data_format='>HHHHHHHH')
        self.logger.debug(f'Data {data} has been sended')

