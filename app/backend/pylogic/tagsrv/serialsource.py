
import time
import os
import binascii
import logging
import serial

from .tagsrv_logger import logger


class DummyPort(object):
    ''' Затычка, чтобы не падало, когда нет такого COM-орта '''
    def write(self, data):
        return len(data)
    def read_all(self):
        return b''
    def read(self, byte_cnt):
        return b''
    def close(self):
        pass
        

class SerialSource(object):
    
    opened_ports = {}
    
    def __init__(self, port=0, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0, xonxoff=False, rtscts=False, name=None):
        if name is None:
            name = f'serial_port_{port}'
        self.logger = logger.getChild(name)
        if port in self.opened_ports:
            raise Exception('Port is opened')
        try:
            self.serial = serial.Serial(
                    port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, xonxoff = xonxoff, rtscts = rtscts)
            self.opened_ports[self.serial.port] = self.serial
            self.name = self.serial.name
            self.logger.info('serial port %s opened', self.serial.name)
        except ValueError:
            self.logger.error(f'Attempt create serial port failed. Bad parameters: {port} {baudrate} {bytesize}-{parity}-{stopbits}')
        except Exception:
            self.logger.exception(f'Attempt crete serial port failed. {port} {baudrate} {bytesize}-{parity}-{stopbits}')
        finally:
            if not hasattr(self, 'serial'):
                self.serial = DummyPort()
                self.name = f'Dummy[{port}]'
        
    def __del__(self):
        self.serial.close()
        
    def read_all(self):
        return self.serial.read_all()
    
    def write(self, data):
        self.logger.debug(f'Serial {self.name} write: hex({binascii.b2a_hex(data)}) ascii({data})')
        self.serial.write(data)
        return True
    
    def read(self, required_bytes=0, timeout=0.2):
        data = b''
        start_time = time.time()
        c=0
        while True:
            c += 1
            # чтение из ком-порта
            data += self.serial.read_all()
            if len(data) >= required_bytes:
                self.logger.debug('Serial %s Read time %.4f count %d', self.name, time.time() - start_time, c)
                break
            if time.time() - start_time > timeout:
                break
            time.sleep(0.001)
        self.logger.debug(f'Serial {self.name} read: hex({binascii.b2a_hex(data)}) ascii({data})')
        return data


if __name__ == '__main__':
    import time
    s = serial.Serial(0, 115200, 8, 'N', timeout=0)
    s.write(b'@02\r')
    i = 1
    t1 = time.time()
    while True:
        res = s.readall()
        if res:
            t2 = time.time()
            s.close()
            print (res, t2 - t1, i + 1)
            break
        i += 1
    