# description of this module in 50 words
# ..



# standard imports
import enum
import random
from threading import Thread
import time

# internal imports
# ..

# component imports
# ..

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..



# ==============================================================================
# TODO : Docs
# ==============================================================================
class Production:

    # docs
    # ==========================================================================
    class State(enum.Enum):
        INACTIVE = -1   # if the production hasn't started even once
        ACTIVE = 0      # if last prod. duration <= cycle_time
        SLOW   = 1      # if last prod. duration <= cycle_time * 1.5
        IDLE   = 2      # if last prod. duration <  breakdown_limit
        BROKEN = 3      # if last prod. duration >= breakdown_limit
        PAUSED = 4      # ...

    # docs
    # --------------------------------------------------------------------------
    def __init__(self, product_name, cycle_time_s, breakdown_limit_s):
        self.__CNAME = "PRODUXN "

        self.__is_requested_stop = True
        self.__is_paused = False
        self.__worker = Thread(target = self.__job)
        
        self.__name  = product_name
        self.__state = self.State.INACTIVE
        self.__cycle_time_s = cycle_time_s
        self.__breakdown_limit_s = breakdown_limit_s
        self.__last_production_time_s = 0
        self.__total_production = 0

    # docs
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        self.__is_paused = False
        self.__is_requested_stop = False
        self.__worker.start()

        # waits to ensure the loop is running
        time.sleep(0.1)

        if self.is_running():
            self.__state = self.State.PAUSED    # activated, but might not be running
            return ERC.SUCCESS
        else:
            return ERC.PRODUCTION_FAILED_TO_START


    # docs
    # --------------------------------------------------------------------------
    def stop(self):
        self.__is_requested_stop = True
        self.__is_paused = False            # clears existing pause reqs (if any)
        self.__worker.join(timeout = 5)     # joins the thread and waits for 5s

        if not self.is_running():
            self.__state = self.State.INACTIVE     # clear if it was ever started
            return ERC.SUCCESS
        else:
            return ERC.PRODUCTION_FAILED_TO_STOP

    # docs
    # --------------------------------------------------------------------------
    def resume(self) -> ERC:
        self.__is_paused = False
        time.sleep(2)             # wait for thread to resume
        return ERC.SUCCESS if self.is_running() else ERC.FAILURE 


    # docs
    # --------------------------------------------------------------------------
    def pause(self):
        self.__is_paused = True
        return ERC.SUCCESS if not self.is_running() else ERC.FAILURE


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return self.__worker.is_alive() and not self.__is_requested_stop and not self.__is_paused


    # This is done because you cannot restart a joined thread
    # --------------------------------------------------------------------------
    def has_started_once(self) -> bool:
        return True if self.__state is not self.State.INACTIVE else False
 

    # docs
    # --------------------------------------------------------------------------
    def get_status(self) -> dict:
        return {
            "name" : self.__name,                                               # str
            "state" : self.__state.value,                                       # enum: INACTIVE, ACTIVE, SLOW, IDLE, BROKEN, PAUSED
            "cycle_time_s" : self.__cycle_time_s,                               # int
            "breakdown_threshold_s" : self.__breakdown_limit_s,                 # int
            "last_production_time_s"  : self.__last_production_time_s,          # int
            "total_production" : self.__total_production                        # int
        }

    # docs
    # --------------------------------------------------------------------------
    def __job(self) -> None:
        while not self.__is_requested_stop:

            start = time.perf_counter()
            self.__total_production += 1
            time.sleep(random.randint(self.__cycle_time_s, self.__breakdown_limit_s + 1))
            end = time.perf_counter()

            self.__last_production_time_s = end - start

            if self.__last_production_time_s <= self.__cycle_time_s:
                self.__state = self.State.ACTIVE
        
            elif self.__last_production_time_s <= (self.__cycle_time_s * 1.5):
                self.__state = self.State.SLOW

            elif self.__last_production_time_s < self.__breakdown_limit_s:
                self.__state = self.State.IDLE

            else:
                self.__state = self.State.BROKEN

            # block this thread if paused
            while self.__is_paused:
                self.__state = self.State.PAUSED
                time.sleep(2)




class Product:

    def __init__(self):
        pass