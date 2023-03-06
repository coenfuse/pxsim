import threading
import time

class Sample:

    def __init__(self):
        self.__is_paused   = threading.Event()
        self.__runtime_t   = threading.Thread(target=self.__job)
        self.__is_req_stop = True


    def start(self):
        self.__is_req_stop = False
        self.__runtime_t.start()


    def stop(self):
        self.__is_req_stop = True
        self.__is_paused.clear()
        self.__runtime_t.join()


    def resume(self):
        self.__is_paused.clear()


    def pause(self):
        self.__is_paused.set()


    def is_running(self):
        return self.__runtime_t.is_alive() and not self.__is_paused.is_set()


    def __job(self):
        while self.__is_req_stop:    
            
            # ..
            time.sleep(4)

            if self.__is_paused.is_set():
                self.__is_paused.wait()