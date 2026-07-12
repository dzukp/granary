from pylogic.supervisor_manager import BaseSupervisor
from pylogic.io_object import IoObject

import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.defines as cst


class ModbusSupervisor(BaseSupervisor):

    def __init__(self, name):
        super().__init__(name)
        self.mb_objects = []
        self.start_addr = 0
        self.length = 0

    def init(self):
        self.mb = modbus_tcp.TcpServer(port=1502, address='0.0.0.0')
        self.mb.start()
        start_addr, end_addr = self.prepare_object(self.top_object)
        if start_addr is not None and end_addr is not None:
            self.start_addr = start_addr
            self.length = end_addr - start_addr + 10
        else:
            self.start_addr = 0
            self.length = 4
        self.slave_1 = self.mb.add_slave(1)
        self.logger.info(f'Create modbus block {start_addr} - {self.length}')
        self.slave_1.add_block('main_hr', block_type=cst.HOLDING_REGISTERS, starting_address=self.start_addr,
                               size=self.length)
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
                if (start_addr is None) or (child_start is not None and child_start < start_addr):
                    start_addr = child_start
                if (end_addr is None) or (child_end is not None and child_end > end_addr):
                    end_addr = child_end
            self.logger.debug(f'{mb_object.full_name} start addr: {start_addr}, end addr: {end_addr} ')
        return start_addr, end_addr

    def receive_data(self):
        data = self.slave_1.get_values('main_hr', self.start_addr, self.length)
        for mb_object in self.mb_objects:
            mb_object.mb_input(self.start_addr, data)
            # cells = mb_object.mb_cells()
            # if 'in' in cells:
            #     for addr, field, format in cells['in']:
            #         mb_object.__dict__[field] = data[addr - self.start_addr]

    def send_data(self):
        data = list(self.slave_1.get_values('main_hr', self.start_addr, self.length))
        for mb_object in self.mb_objects:
            for addr, val in mb_object.mb_output(self.start_addr).items():
                data[addr] = val
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
