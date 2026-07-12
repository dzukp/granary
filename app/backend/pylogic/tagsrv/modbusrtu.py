import time
import struct

from .tagsrv_logger import logger
from .module import BaseModule


__all__ = ['ModbusRTUModule',]


def u16_to_bestr(u):
    """Given word, return as big-endian binary"""
    u = (u & 0xFFFF)
    return u >> 8 + u & 0xFF


def crc16(input_data: bytes):
    """Calculate CRC-16 for Modbus.
    
    Args:
        input_data (bytes): An arbitrary-length message (without the CRC).

    Returns:
        A two-byte CRC string, where the least significant byte is first.
    
    Algorithm from the document 'MODBUS over serial line specification and implementation guide V1.02'.
    
    """
    # Constant for MODBUS CRC-16
    poly = 0xA001
 
    # Preload a 16-bit register with ones
    register = 0xFFFF
    
    for byte in input_data:
        # XOR with each character
        register = register ^ byte
        for i in range(8):
            if register & 0x01:
                register = (register >> 1) ^ poly
            else:
                register = (register >> 1)
    return struct.pack('H', register)
    

class ModbusRTUModule(BaseModule):
    """ Модуль ModBus RTU """
    
    class InTagRequest(object):
        def __init__(self, slave, tags):
            def sort_key(tag):
                return tag.addr
            self.tags = tags
            self.tags.sort(key=sort_key)
            addr = self.tags[0].addr
            # self.req = chr(slave) + chr(0x3) + \
            #             u16_to_bestr(addr) + \
            #             u16_to_bestr(len(self.tags))
            # self.req += crc16(self.req)
            self.req = struct.pack('>BBHH', slave, 0x3, addr, len(self.tags))
            self.req += crc16(self.req)
            #self.ans = chr(slave) + chr(0x3)
            self.ans = struct.pack('BB', slave, 0x3)
            self.ans_len = 5 + len(self.tags) * 2
            
        def generate(self):
            return self.req
        
        def is_ans_valid(self, ans):
            if ans[:2] != self.ans:
                return False
            if len(ans) != self.ans_len:
                return False
            return True
        
        def ans_process(self, ans):
            quant = len(self.tags)
            data = struct.unpack(f'>{"H" * quant}', ans[3:3 + quant * 2])
            for tag, value in zip(self.tags, data):
                if tag.filter:
                    tag.value = tag.filter.apply(value)
                else:
                    tag.value = value
            # i = 0
            # for tag in self.tags:
            #     a = ord(ans[3 + i])
            #     b = ord(ans[4 + i])
            #     value = (a << 8) + b
            #     if tag.filter:
            #         tag.value = tag.filter.apply(value)
            #     else:
            #         tag.value = value
            #     i += 2
        
    class OutTagRequest(object):
        def __init__(self, slave, tags):
            def sort_key(tag):
                return tag.addr
            self.tags = tags
            self.tags.sort(key=sort_key)
            addr = self.tags[0].addr
            # self.req = chr(slave) + chr(0x10) + \
            #             u16_to_bestr(addr) + \
            #             u16_to_bestr(len(self.tags)) + \
            #             chr(len(self.tags) * 2)
            # self.ans = chr(slave) + chr(0x10) + \
            #             u16_to_bestr(addr) + \
            #             u16_to_bestr(len(self.tags))
            self.req = struct.pack('>BBHHB', slave, 0x10, addr, len(self.tags), len(self.tags) * 2)
            self.ans = struct.pack('>BBHH', slave, 0x10, addr, len(self.tags))
            self.ans_len = 8
            
        def generate(self):
            values = []
            for tag in self.tags:
                if tag.filter:
                    val = tag.filter.apply(tag.value)
                else:
                    val = tag.value
                values.append(int(val))
            data = struct.pack('>' + ('H' * len(self.tags)), *values)
            result = self.req + data
            result += crc16(result)
            return result
        
        def is_ans_valid(self, ans):
            return ans[:6] == self.ans
        
        def ans_process(self, ans):
            pass
            
    class OutTagRequestFunc0(object):
        def __init__(self, slave, tags):
            self.tags = tags
            self.tags.sort(key=lambda t: t.addr)
            addr = self.tags[0].addr
            self.req = chr(slave) + chr(0x10) + \
                        u16_to_bestr(addr) + \
                        u16_to_bestr(len(self.tags)) + \
                        chr(len(self.tags) * 2)
            self.ans = chr(slave) + chr(0x10) + \
                        u16_to_bestr(addr) + \
                        u16_to_bestr(len(self.tags))
            self.ans_len = 8
            
        def generate(self):
            data = ''
            for tag in self.tags:
                if tag.filter:
                    val = tag.filter.apply(tag.value)
                else:
                    val = tag.value
                data += u16_to_bestr(val)
            result = self.req + data
            result += crc16(result)
            return result
        
        def is_ans_valid(self, ans):
            return ans[:6] == self.ans
        
        def ans_process(self, ans):
            pass

    def __init__(self, slave, serial, in_tags=tuple(), out_tags=tuple(), io_tags=tuple(), max_answ_len=16, timeout=0.1):
        super(ModbusRTUModule, self).__init__(name=f'{serial.name} #{slave}')
        self.slave = slave
        self.serial = serial
        self.max_answ_len = max_answ_len
        self.timeout = timeout
        self.tags = in_tags + io_tags + out_tags
        in_tags = self._forming_tag_list(list(in_tags + io_tags))
        out_tags = self._forming_tag_list(list(out_tags + io_tags))
        self.ireqs = []
        self.oreqs = []
        for tags in in_tags:
            self.ireqs.append(self.InTagRequest(slave, tags))
        for tags in out_tags:
            self.oreqs.append(self.OutTagRequest(slave, tags))
        self.err_cnt = 0
        self.logger = logger
        
    def _forming_tag_list(self, taglist):
        taglist.sort(key=lambda tag: tag.addr)
        formed_taglist = []
        last_tag_idx = 0
        while last_tag_idx < len(taglist):
            # Формирование последовательности ячеек длинной не более 16 ячеек
            # по стандарту Modbus за 1 посылку можно передать только 16 ячеек
            begin_addr = taglist[last_tag_idx].addr
            tmp_tags = []
            for tag in taglist[last_tag_idx:]:                
                if tag.addr - begin_addr >= self.max_answ_len:
                    break
                last_tag_idx += 1
                tmp_tags.append(tag)
            if tmp_tags:
                formed_taglist.append(tmp_tags)
        return formed_taglist

    def set_logger(self, logger):
        self.logger = logger

    def _value_to_str(self, value):
        return f'{int(value):04x}' if value is not None else '----'
        
    def process(self):
        self.serial.read_all()
        i = 0
        #first_start_time = time.time()
        ok = False
        for req in self.ireqs + self.oreqs:
            i += 1
            try:
                #start_time = time.time()
                self.send(req)
                self.receive(req)
                #print i, 'send - receive timeout', time.time() - start_time
            except Exception as e:
                self.logger.error(e)
            else:
                ok = True
            time.sleep(0.005)
        self.ok = ok
        if ok:
            self.last_ok = time.time()
        #print 'all_cycle', time.time() - first_start_time
    
    def send(self, req):
        request = req.generate()
        self.logger.debug(f'Send {[hex(x) for x in request]}')
        if not self.serial.write(request):
            self.err_cnt += 1
            raise Exception('Slave %d (ModBus RTU): Send error (%d)' % (self.slave, self.err_cnt))
    
    def receive(self, req):
        result = self.serial.read(req.ans_len, self.timeout)[-req.ans_len:]
        self.logger.debug(f'Receive {[hex(x) for x in result]}')
        if req.is_ans_valid(result):
            # Обработка ответа ПЧ
            req.ans_process(result)
            return True
        else:
            self.err_cnt += 1
            self.logger.error('Slave %d (ModBus RTU): Receive error (%d), serial read result `%s` request `%s`' % \
                    (self.slave, self.err_cnt, [hex(r) for r in result], [hex(r) for r in req.generate()]))
            raise Exception('Slave %d (ModBus RTU): Receive error ModBus RTU' % self.slave)


if __name__ == '__main__':
    print([hex(x) for x in crc16(b'\x01\x06\x80\x00\x00\x00')])
    from .tagsrv import Tag
    it = [Tag(addr=i) for i in range(8)]
    it += [Tag(addr=i) for i in range(15,20)]
    rtu_module = ModbusRTUModule(1, None, in_tags=it, out_tags=[])
    print('end')

