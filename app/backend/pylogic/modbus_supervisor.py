import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
from pylogic.io_object import IoObject
from pylogic.supervisor_manager import BaseSupervisor


class ModbusSupervisor(BaseSupervisor):
    def __init__(self, name):
        super().__init__(name)
        self.mb_objects = []
        self.start_addr = 0
        self.length = 0
        self.mb = None
        self.slave_1 = None

    def init(self):
        self.mb = modbus_tcp.TcpServer(port=1502, address='0.0.0.0')
        start_addr, end_addr = self.prepare_object(self.top_object)
        if start_addr is not None and end_addr is not None:
            self.start_addr = start_addr
            self.length = end_addr - start_addr + 20
        else:
            self.start_addr = 0
            self.length = 20
        self.slave_1 = self.mb.add_slave(1)
        self.logger.info(f'Create modbus block {start_addr} - {self.length}')
        self.slave_1.add_block(
            'main_hr',
            block_type=cst.HOLDING_REGISTERS,
            starting_address=self.start_addr,
            size=self.length,
        )
        self.mb.start()
        self.send_data()

    def prepare_object(self, mb_object):
        start_addr = None
        end_addr = None
        if isinstance(mb_object, ModbusDataObject):
            self.mb_objects.append(mb_object)
            cells = mb_object.mb_cells()
            if cells and (start_addr is None or min(cells) < start_addr):
                start_addr = min(cells)
            if cells and (end_addr is None or max(cells) > end_addr):
                end_addr = max(cells)
        if isinstance(mb_object, IoObject):
            for child in mb_object.children:
                child_start, child_end = self.prepare_object(child)
                if (start_addr is None) or (
                    child_start is not None and child_start < start_addr
                ):
                    start_addr = child_start
                if (end_addr is None) or (
                    child_end is not None and child_end > end_addr
                ):
                    end_addr = child_end
            self.logger.debug(
                f'{mb_object.full_name} start addr: {start_addr}, end addr: {end_addr} ',
            )
        return start_addr, end_addr

    def receive_data(self):
        data = self.slave_1.get_values('main_hr', self.start_addr, self.length)
        for mb_object in self.mb_objects:
            mb_object.mb_input(self.start_addr, data)

    def _clamp(self, value: int, lo: int = 0, hi: int = 65535):
        if value < lo or value > hi:
            self.logger.error(
                f'Value {value} out of range [{lo}, {hi}], clamping to {max(lo, min(hi, value))}',
            )
            return max(lo, min(hi, value))
        else:
            return value

    def send_data(self):
        data = list(
            self.slave_1.get_values(
                'main_hr',
                self.start_addr,
                self.length,
            ),
        )
        for mb_object in self.mb_objects:
            for addr, val in mb_object.mb_output(self.start_addr).items():
                data[addr] = self._clamp(val)
        self.slave_1.set_values('main_hr', self.start_addr, data)


class ModbusDataObject:
    # def mb_cells(self):
    #     """ Return dict, format:
    #     {
    #         'in': [<data>, ...],
    #         'out': [<data>, ...]
    #     }
    #     """
    #     return {'in': [], 'out': []}

    def mb_cells(self):
        return self.mb_output(0).keys()

    def mb_input(self, start_addr, data):
        pass

    def mb_output(self, start_addr):
        return {}
