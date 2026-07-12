import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading

from pylogic.io_object import IoObject
from pylogic.supervisor_manager import BaseSupervisor
from pylogic.logged_object import LoggedObject


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class MyXMLRPCServer(SimpleXMLRPCServer):
    def process_request(self, request, client_address):
        self.client_address = client_address
        return SimpleXMLRPCServer.process_request(
            self, request, client_address)


class RpcServer(LoggedObject):
    def __init__(self):
        super().__init__('RpcServer')
        self.set_logger(self.logger.getChild('rpc_post_server'))
        self.top_object = None
        self.tag_srv = None
        self.server_thread = None
        self.host = ('127.0.0.1', 9876)

        self.post_state = LoggedObject('PostState')
        self.post_state.set_logger(self.post_state.logger.getChild('rpc_post_state'))

    def set_top_object(self, top_object: IoObject):
        self.top_object = top_object

    def set_tag_server(self, tag_srv):
        self.tag_srv = tag_srv

    def start(self):
        self.server_thread = threading.Thread(target=self.run, name='RpcServer', daemon=True)
        self.server_thread.start()

    def run(self):
        with MyXMLRPCServer(self.host, requestHandler=RequestHandler, logRequests=False) as server:
            server.register_introspection_functions()

            @server.register_function
            def get_tagsrv_modules_state():
                modules = []
                for disp in self.tag_srv.dispatchers.values():
                    for m in disp.modules:
                        try:
                            values = m.tag_values()
                        except Exception as ex:
                            values = 'EXC'
                        modules.append({
                            'name': m.name,
                            'ok': m.ok,
                            'last_ok': round(time.time() - m.last_ok, 3),
                            'tags': values
                        })
                return modules

            server.register_multicall_functions()
            server.serve_forever()


class RpcSupervisor(BaseSupervisor):

    def __init__(self, name):
        super().__init__(name)
        self.rpc_server = RpcServer()

    def init(self):
        self.rpc_server.set_top_object(self.top_object)
        self.rpc_server.set_tag_server(self.tag_srv)
        self.rpc_server.start()

    def receive_data(self):
        pass

    def send_data(self):
        pass
