import threading
from threads.server.diag_th import runtime_diag_check

class ThreadManager:
    def __init__(self, diag, logger, utilG, arg_interval):
        self.threads = []
        self.stop_events = []
        self.diag = diag
        self.logger = logger
        self.utilG = utilG
        
    def essential_threds(self, interval):
        self.start_thread(target=runtime_diag_check, args=(self.diag, self.logger, self.utilG), kwargs={"interval": interval})
    
    def start_thread(self, target, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        stop_event = threading.Event()
        kwargs = dict(kwargs)
        kwargs["stop_event"] = stop_event
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        thread.start()
        self.threads.append(thread)
        self.stop_events.append(stop_event)

    def stop_all(self):
        for event in self.stop_events:
            event.set()
        for thread in self.threads:
            thread.join()