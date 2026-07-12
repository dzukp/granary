
import threading
import time
import logging



class ModuleDispatcher(threading.Thread):

    def __init__(self, modules, timeout=0.005):
        super().__init__()
        self.setDaemon(True)
        if not modules:
            raise Exception('Module dispatcher has no modules')
        self.modules = modules
        self.timeout = timeout
        self.logger = logging.getLogger('TagSrv')

    def set_logger(self, logger):
        self.logger = logger
        
    def onStart(self):
        self.logger.info('OnStart')
    
    def process(self):
        pass
    
    def run(self):
        self.onStart()
        while True:
            try:
                t1 = time.time()
                self.process()
                cycle_time = time.time() - t1
                self.logger.info('XModuleDispatcher cycle_time %.4f' % cycle_time)
                time.sleep(max(0.0001, self.timeout - cycle_time))
            except Exception as ex:
                self.logger.error(ex)
                time.sleep(self.timeout)
    
    def profiler_run(self):
        
        import cProfile, profile
        import pstats
        
        def profile_main():
            def main():        
                self.onStart()
                count = 0
                while count < 1000:
                    count += 1
                    try:
                        t1 = time.time()
                        self.process()
                        cycle_time = time.time() - t1
                        #print 'XModuleDispatcher cycle_time',cycle_time
                        time.sleep(max(0.0001, self.timeout - cycle_time))
                    except Exception as ex:
                        print(ex)
                        time.sleep(self.timeout)
                        
            prof = cProfile.Profile()
            prof = prof.runctx("main()", globals(), locals())
            print("<pre>")
            stats = pstats.Stats(prof)
            stats.sort_stats("time")  # Or cumulative
            stats.print_stats(80)  # 80 = how many to print
            print("</pre>")
                    
        profile_main()
    
    
class SerialDispatcher(ModuleDispatcher):
    
    def __init__(self, modules, timeout=0.005):
        super().__init__(modules=modules, timeout=timeout)
        self.current_module = None
        self.current_idx = 0
        
    def onStart(self):
        super(SerialDispatcher, self).onStart()
        self.current_module = self.modules[self.current_idx]
        
    def process(self):
        try:
            self.logger.debug('Module %d' % self.current_idx)
            self.current_module.process()
        except Exception as e:
            self.logger.exception('Module error: %s' % e)
        self.current_idx = (self.current_idx + 1) % len(self.modules)
        self.current_module = self.modules[self.current_idx]
        

class ParallelDispatcher(ModuleDispatcher):

    def __init__(self, modules, timeout=0.05):
        super().__init__(modules, timeout)

    def start(self):
        for module in self.modules:
            module_thread = threading.Thread(target=module.loop)
            module_thread.setDaemon(True)
            module_thread.start()

    def process(self):
        while True:
            time.sleep(self.timeout)