
import sys
#import time
import threading
import code
import traceback
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from rlcompleter import Completer


class FileCacher:
    """ Запоминатель текста """
    
    def __init__(self): 
        self.reset()
        
    def reset(self): 
        self.out = []
        
    def write(self,line): 
        self.out.append(line)
        
    def flush(self):
        output = ''.join(self.out)
        self.reset()
        return output


class MyInterpreter(code.InteractiveInterpreter):

    def showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it is our own code.

        The output is written by self.write(), below.

        """
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        try:
            lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
            if sys.excepthook is sys.__excepthook__:
                self.write(''.join(lines))
            else:
                # If someone has set sys.excepthook, we let that take precedence
                # over self.write
                # sys.excepthook(ei[0], ei[1], last_tb)
                self.write(''.join(lines))
                pass
        finally:
            last_tb = ei = None


class PylogicRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class ShellXMLRPCServer(SimpleXMLRPCServer):
    def __init__(self, addr, requestHandler=PylogicRequestHandler, locals=None):
        self.completer = Completer(locals)
        SimpleXMLRPCServer.__init__(self,addr, requestHandler, logRequests=False, allow_none=False, encoding=None, bind_and_activate=True)
        self.register_introspection_functions()
        
        self.register_function(self.interpreter_function, 'interpreter')
        self.register_function(self.completer_function, 'completer')
        self.register_function(self.dr_function, 'dump_receiver')
        self.register_function(self.dump_channels_function, 'dump_channels')
        
        self.cache = FileCacher()
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.buffer = []
        self.filename = "<console>"
        self.locals = locals
        #self.interpreter = code.InteractiveInterpreter(self.locals)
        self.interpreter = MyInterpreter(self.locals)
        
    def get_output(self): 
        """ Захватить вывод """
        sys.stdout = self.cache
        sys.stderr = self.cache
        
    def return_output(self): 
        """ Отпустить вывод """
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        
    def interpreter_function(self,line):
        """ Выполнение line в интерпретаторе """
        self.get_output()
        
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.interpreter.runsource(source, self.filename)
        if not more:
            self.resetbuffer()

        self.return_output()

        output = self.cache.flush()
        return output, more

    def resetbuffer(self):
        """ Reset the input buffer """
        self.buffer = []
    
    def completer_function(self,text,state):
        return self.completer.complete(text, state)
    
    def dr_function(self,addr):
        """ Prints receiver attributes. Usage: dr addr """
        self.get_output()
        obj = self.locals['app'].getTopManager().getObjByAddr(addr)
        for attr in dir(obj):
            if not attr.startswith('__'):
                try:
                    if obj.__dict__[attr].__class__.__name__ in ['str','bool','int']:
                        print(str(attr) + ' => '+str(obj.__dict__[attr]))
                    if obj.__dict__[attr].__class__.__name__ == 'XChannel':
                        print(str(attr) + ' => ' + str(obj.__dict__[attr].value))
                except:
                    pass
        self.return_output()
        return self.cache.flush()
    
    def dump_channels_function(self,type,name=None):
        """ Prints input chanels. Usage: TYPE NAME """
        self.get_output()
        
        res = []
        if type == 'in':
            self.locals['app'].getTopManager().dumpInputChanels(res)
        else:
            self.locals['app'].getTopManager().dumpOutputChanels(res)
        
        for a in res:
            for x in a: 
                if not x.startswith('Sim'):
                    if name:
                        if x == name:
                            print(x)
                            print('--------------')
                            for j in a[x]:
                                print(j['name']+' => '+str(j['value']))
                            print("")
                    else:
                        print(x)
                        print('--------------')
                        for j in a[x]:
                            print(j['name']+' => '+str(j['value']))
                        print("")

        self.return_output()
        return self.cache.flush()


def start_shell_server(namespace, host=("0.0.0.0", 9999)):
    import threading
    server = ShellXMLRPCServer(host, locals=namespace)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setName('Shell')
    server_thread.setDaemon(True)
    server_thread.start()
    

if __name__ == '__main__':
    server = ShellXMLRPCServer(("*", 10000), requestHandler = PylogicRequestHandler,locals=locals())
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    while 1:
        pass