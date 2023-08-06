# description of this module in 50 words
# ..



# standard imports
import enum
import random
import threading
import time
from typing import Dict

# internal imports
from source.apps.pluxsim.simulator.internal.production import Production
from source.apps.pluxsim.simulator.internal.production import Product

# component imports
# ..

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..



# ==============================================================================
# TODO : explain docs
# ==============================================================================
class Machine:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self, name: str):
        self.__CNAME = "MACHINE "
        self.__name = name
        self.__productions: Dict[str, Production] = {}


    # docs
    # --------------------------------------------------------------------------
    def add_production(self, for_product, cycle_time_s, breakdown_threshold_s) -> ERC:
        if self.has_production(for_product):
            return ERC.PRODUCTION_ALREADY_EXISTS
        else:
            self.__productions[for_product] = Production(for_product, cycle_time_s, breakdown_threshold_s)
            return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def has_production(self, product) -> bool:
        return True if product in self.__productions else False


    # docs
    # --------------------------------------------------------------------------
    def remove_production(self):
        pass


	# Starts the default production unless specific production is mentioned
	# Whenever a non-default production is started, it becomes the default
	# one. This allows simpler management of default-idle and 
	# non-default-runtime productions.
    # --------------------------------------------------------------------------
    def start_production(self, for_product = None) -> ERC:
        
        # are there even any productions available?
        status = ERC.PRODUCTION_NOT_FOUND if len(self.__productions) == 0 else ERC.SUCCESS

        # check if specific production is mentioned
        if status is ERC.SUCCESS:

                if for_product in self.__productions:
                    status = self.__productions[for_product].start()
        
                # start the first production from the production list
                # what's going on?
                # dict.items() gives us an iteration list for all the items in
                # a dictionary where every individual item is a tuple of key-val
                # pair. next() gives us the first iterator here, but to use that,
                # we need to explicitly type cast the iteration list to iter()
                # Once next() gives us the tuple, we access the value part of it
                # here, type:Production with index mapping [1]. One we have our
                # production, we can use that production obj to start the production
                # in this machine
                else:
                    first_production = next(iter(self.__productions.items()))[1]
                    status = first_production.start()

        return status


    # docs
    # --------------------------------------------------------------------------
    def stop_production(self, for_product = None) -> ERC:

        # are there even any production available?
        status = ERC.PRODUCTION_NOT_FOUND if len(self.__productions) <= 0 else ERC.SUCCESS

        if status is ERC.SUCCESS:

            # stop the specific production for product if exist
            if for_product in self.__productions:
                status = self.__productions[for_product].stop()

            # else stop all productions
            else:
                if all(production.stop() is ERC.SUCCESS for production in self.__productions.values()):
                    status = ERC.SUCCESS
                else:
                    status = ERC.PRODUCTION_FAILED_TO_STOP

        return status


    # docs
    # --------------------------------------------------------------------------
    def resume_production(self, for_product = "") -> ERC:
        if len(for_product) == 0:
            return ERC.SUCCESS if all(a_prod.resume() for a_prod in self.__productions.values()) else ERC.PRODUCTION_FAILED_TO_RESUME
        if for_product in self.__productions:
            return self.__productions[for_product].resume()
        else:
            return ERC.PRODUCTION_NOT_FOUND


    # docs
    # --------------------------------------------------------------------------
    def pause_production(self, for_product = "") -> ERC:
        if len(for_product) == 0:
            return ERC.SUCCESS if all(a_prod.pause() for a_prod in self.__productions.values()) else ERC.PRODUCTION_FAILED_TO_PAUSE
        elif for_product in self.__productions:
            return self.__productions[for_product].pause()
        else:
            return ERC.PRODUCTION_NOT_FOUND


	# Is true if atleast one production is running in the machine
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return any(production.is_running() for production in self.__productions.values())


	# You get status for machine if no production is mentioned.
	# machine and production status schemas are different
    # --------------------------------------------------------------------------
    def get_status(self, for_product = "") -> dict:
        
        # default schema for a machine
        response = {
            "name" : None,                                                      # str
            "is_running" : False,                                               # bool
            "productions" : None,                                               # list(str)
            "active_production" : ""                                            # str / None
        }

        # get status of a specific production
        if self.has_production(for_product):
            response = self.__productions[for_product].get_status()
        
        # else fill out the status for this machine
        else:
            response["name"] = self.__name
            response["is_running"] = self.is_running()
            response["productions"] = list(self.__productions.keys())
            
            for product_name, production in self.__productions.items():
                if production.has_started_once() and production.is_running():   # a production has to be started once before and running (not paused) before checking for active status
                    if production.get_status()["state"] < 3:                    # a production has to be ACTIVE, SLOW or IDLE to be counted as active production
                        response["active_production"] = product_name

        return response


    # docs
    # --------------------------------------------------------------------------
    def switch_production(self, to_product) -> ERC:
        
        # first find if the product we wish to switch to even exists or not?
        if to_product in self.__productions:

            # get the currently active production and pause it (not stop)
            for a_production in self.__productions.values():
                if a_production.is_running():
                    a_production.pause()                                        # we dont care if it was paused or not (why?)
                    break                                                       # we just dont
            
            # then,
            if self.__productions[to_product].has_started_once():
                return self.__productions[to_product].resume()                  # resume if previously paused
            else:
                return self.__productions[to_product].start()                   # clean start

        # can switch to desired production, as it does not exist on this machine
        else:
            return ERC.PRODUCTION_NOT_FOUND




class Machine_T:

    # ==========================================================================
    class STATE(enum.Enum):
        INACTIVE = -1   # if machine hasn't started even once
        ACTIVE = 0      # if machine's last production duration <= cycle_time_s of the active product
        SLOW   = 1      # if machine's last production duration <= cycle_time_s * 1.5 of the active product
        IDLE   = 2      # if machine's last production duration <  breakdown threshold_s of the active product
        BROKEN = 3      # if machine's last production duration >= breakdown_threshold_s
        PAUSED = 4      # if machine is paused


    # docs
    # --------------------------------------------------------------------------
    def __init__(self, name: str, breakdown_pct: float = 0.0, total_production_init: int = 0):
        self.__CNAME = "MACHINE "
        self.__name  = name

        self.__is_requested_stop = True
        self.__is_paused = False
        self.__runtime = threading.Thread(target = self.__job)
        self.__runtime.name = f"machine_{name}_runtime"

        self.__active_production = ""
        self.__active_prod_lock  = threading.Lock()
        self.__breakdown_pct = breakdown_pct if (breakdown_pct <= 100.0) and (breakdown_pct >= 0.5) else 0.5
        self.__state = self.STATE.INACTIVE
        self.__last_production_duration_s = 0
        self.__total_production = total_production_init

        self.__db = {}

    # docs
    # --------------------------------------------------------------------------
    def add_product(self, product_name, cycle_time_s, breakdown_threshold_s) -> ERC:
        if product_name not in self.__db:
            product = self.__get_product_schema(product_name, cycle_time_s, breakdown_threshold_s)
            self.__db[product_name]  = product          # add product to DB
            self.__active_production = product_name     # set this for active production, this will ensure the last added product will be produced on started unless stated otherwise
            return ERC.SUCCESS
        else:
            return ERC.PRODUCTION_ALREADY_EXISTS     
        

    # docs
    # --------------------------------------------------------------------------
    def remove_product(self, product_name) -> ERC:
        if product_name in self.__db:
            self.__db.pop(product_name)
            return ERC.SUCCESS
        else:
            return ERC.PRODUCTION_NOT_FOUND


    # docs
    # --------------------------------------------------------------------------
    def has_product(self, product_name) -> bool:
        return True if product_name in self.__db else False


    # docs
    # --------------------------------------------------------------------------
    def start(self, production_for = None) -> ERC:
        self.__is_paused = False
        self.__is_requested_stop = False

        # start production for a specific product (if mentioned)
        if production_for in self.__db:
            self.__active_production = production_for

        self.__runtime.start()

        # waits to ensure the runtime is active
        time.sleep(0.1)

        if self.is_running():
            return ERC.SUCCESS
        else:
            return ERC.MACHINE_FAILED_TO_START


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        self.__is_requested_stop = True
        self.__is_paused = False                # clears existing pause blocks (if any)
        self.__runtime.join(timeout = 5)        # joins the thread and waits for 5 seconds max.

        if not self.is_running():
            self.__state = self.STATE.INACTIVE  # clears as if it wasn't ever started
            return ERC.SUCCESS
        else:
            return ERC.MACHINE_FAILED_TO_STOP


    # resumes a paused machine, # TODO : Use CV here
    # --------------------------------------------------------------------------
    def resume(self) -> ERC:
        self.__is_paused = False
        time.sleep(2)               # wait for thread to resume
        return ERC.SUCCESS if self.is_running() else ERC.MACHINE_FAILED_TO_RESUME


    # pauses a machine, # TODO : Use CV here
    # --------------------------------------------------------------------------
    def pause(self) -> ERC:
        self.__is_paused = True
        time.sleep(1)               # wait for thread to pause
        return ERC.SUCCESS if not self.is_running() else ERC.MACHINE_FAILED_TO_PAUSE


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> ERC:
        return self.__runtime.is_alive() and not self.__is_requested_stop and not self.__is_paused


    # docs
    # --------------------------------------------------------------------------
    def get_status(self, product_name = "") -> dict:
        
        # default schema for a machine
        response = {
            "name" : None,                                                      # str
            "is_running" : False,                                               # bool
            "products"  : None,                                                 # list(str)
            "active_production" : "",                                           # str / None
            "breakdown_percentage" : None,                                      # float
            "state" : None,                                                     # str
            "total_production" : 0,                                             # int
            "last_production_duration_s" : 0                                    # float
        }

        # get status for a specific production:
        if product_name in self.__db:
            response = self.__db[product_name]

        # else fill out the status for this machine
        else:
            response["name"] = self.__name,
            response["state"] = f"{self.__state.value} [{self.__state.name}]"
            response["is_running"] = self.is_running(),
            response["products"] = list(self.__db.keys())
            response["active_production"] = self.__active_production
            response["breakdown_percentage"] = self.__breakdown_pct
            response["last_production_duration_s"] = self.__last_production_duration_s
            response["total_production"] = self.__total_production

            # PATCH : Very strange bug, the self.__name and self.is_running()
            # variable assign themselves as tuple in response["name"] and
            # response["is_running"] which in turn corrupts the response string
            # as the tuple gets translated into list. I DO NOT KNOW WHY.
            # 
            # As a patch fix, I have to reassign, response['name'] with its
            # own tuple index. This somehow fixes the thing. The hell is this.
            response["name"] = response["name"][0]
            response["is_running"] = response["is_running"][0]
            
        return response

    
    # docs
    # --------------------------------------------------------------------------
    def switch(self, to_product) -> ERC:
        if to_product in self.__db:
            self.__active_prod_lock.acquire(blocking = True)
            self.__active_production = to_product
            self.__active_prod_lock.release()
            return ERC.SUCCESS
        else:
            return ERC.PRODUCTION_NOT_FOUND


    # docs
    # -------------------------------------------------------------------------- 
    def __get_product_schema(self, name, cycle_time_s, breakdown_threshold_s) -> dict:
        return {
            "name" : name,
            "cycle_time_s" : cycle_time_s,
            "breakdown_threshold_s" : breakdown_threshold_s,
            "last_production_duration_s" : 0,
            "total_production" : 0
        }


    # docs
    # --------------------------------------------------------------------------
    def __job(self) -> ERC:
        while not self.__is_requested_stop:
            
            self.__active_prod_lock.acquire()
            product_name = self.__active_production
            self.__active_prod_lock.release()

            start = time.perf_counter()
            product = self.__db.get(product_name)
            self.__produce(product)
            end   = time.perf_counter()

            self.__last_production_duration_s = round(end - start, 3)                   # for machine level status report
            product["last_production_duration_s"] = self.__last_production_duration_s   # for product level status report

            self.__evaluate_machine_status(self.__last_production_duration_s, product)
            self.__db[product_name] = product

            # block this thread if paused # TODO : USE CV here!
            while self.__is_paused:
                self.__state = self.STATE.PAUSED
                time.sleep(1)


    # docs
    # --------------------------------------------------------------------------
    def __produce(self, product: dict) -> dict:

        # finds the range between min and max + 1, (100 + 1) - 10 = 91
        # +1 because the range generated here will be used for artifically managing
        # the production time, and since a machine will be marked as broken when
        # the production time goes beyond max limit (here, refers to breakdown_threshold_s)
        # so we need to have a range the generates value beyond brkdwn threshold
        # NOTE : Consider -1 the min value as well
        range = (product['breakdown_threshold_s'] + 1) - product['cycle_time_s']
        
        # The distribution point (distp) gives us the absolute point of distribution
        # within our calculated range. Since, our randomness generator allows
        # bias for randomness distribution, the distp here tells us the amount
        # of bias we need to what end.
        # So with self.__breakdown_pct of 86% and range of 91 betwee 10 and 101,
        # the distribution point will be, 
        # 86% * 91 + 10 = 78.26 + 10 = 88.26 ~ 88
        # So the random generator here will generate random values between 10
        # and 101, but most of the generators would be 88 or ateast near it.
        distp = range * (self.__breakdown_pct / 100) + product['cycle_time_s']
        distp = round(distp)

        # Use the distribution curve to generate sleep amount in seconds which
        # are then used for sleeping this thread. Simulating production time.
        time.sleep(random.triangular(
            low = product["cycle_time_s"],
            high = product["breakdown_threshold_s"],
            mode = distp))

        # produce the actual product by incrementing its produce (lol)
        product['total_production'] += 1

        # increment the total production made by this machine considering all
        # products
        self.__total_production += 1


    # docs
    # --------------------------------------------------------------------------
    def __evaluate_machine_status(self, last_duration, product):
        
        lb = product['cycle_time_s']
        ub = product['breakdown_threshold_s']

        # Range is the machine's production time limit within its promised cycle
        # time and breakdown threshold. 
        # Say a machine can produce a product ideally in 5s and will be marked 
        # as broken, if its production cycle exceeds 15s i.e., breakdown threshold.
        # So, here the working range is brkdwn_threshold - cycle_time = 15 - 5 = 10s
        range = ub - lb

        # Now if duration of last production covers less than 25% of operative
        # range, we mark this as tolerable zone and the machine status is marked
        # as active. Here, following with the above example,
        # Any production duration that is less than 7.5s is marked as ACTIVE
        # lb + range * 0.25 = 5 + 10 * 0.25 = 5 + 2.5 = 7.5s
        if last_duration < (lb + range * 0.25):
            self.__state = self.STATE.ACTIVE

        # Any production duration below 5 + 10 * 0.5 = 10s is marked, SLOW
        elif last_duration < (lb + range * 0.5):
            self.__state = self.STATE.SLOW

        # Any production duration below 15s is marked, IDLE
        elif last_duration < ub:
            self.__state = self.STATE.IDLE

        # Any production that is equal or beyond upper bound is marked, BROKEN
        else:
            self.__state = self.STATE.BROKEN