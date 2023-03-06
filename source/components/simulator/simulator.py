# description of this module in 50 words
# ..



# standard imports
import json
import math
import random
import threading
import time
from typing import Dict

# internal imports
from source.components.simulator import schema as SchemaFactory
from source.components.simulator.status import PSSC

# component imports
from source.components.io import logger

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..



# ==============================================================================
# Let's say, for a product in a machine, cycle_time is 5s & idle_limit is 10s
#
# So, a machine is said to,
# ACTIVE    -> if production_time <= cycle_time
# IDLE      -> if production_time > cycle_time AND production_time <= idle_limit
# BREAKDOWN -> if production_time > idle_limit
# 
# ==============================================================================
class Simulator:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__NAME = "PXSIM   "
        self.__machines: Dict[str, self.__Machine] = {}

    
    # docs
    # --------------------------------------------------------------------------
    def add_production(self,
        product: str,           # name of the product to be created
        machine: str,           # name of the machine to be used for it (will be created if not exists)
        cycle_time_s: int,      # the ideal manufacture time of this product, can be faster.
        idle_limit_s: int       # if manufacture time is between cycle_time_s and idle_time_s, the machine will be marked IDLE. If manufacture time is beyond idle_time_s, machine is in BREAKDOWN
    ) -> ERC:
    
        status = ERC.SUCCESS
        reason = ""
        
        logger.trace(" ")    # cosmetic separator for trace logs
        logger.debug(f"{self.__NAME} : adding new production for {product} in {machine}")
        logger.trace(f"{self.__NAME} : searching for {machine} in machine list")
    
        if machine in self.__machines:
            logger.trace(f"{self.__NAME} : {machine} was found")
            logger.debug(f"{self.__NAME} : updating machine {machine}")
            
            status = self.__machines[machine].add_production(
                product, 
                cycle_time_s, 
                idle_limit_s)
        
        else:
            logger.trace(f"{self.__NAME} : {machine} was not found")
            logger.debug(f"{self.__NAME} : adding new machine {machine}")
            
            self.__machines[machine] = self.__Machine(machine)
            status = self.__machines[machine].add_production(
                product,
                cycle_time_s,
                idle_limit_s)

        if status is ERC.SUCCESS:
            logger.info(f"{self.__NAME} : SUCCESS - production added for {product} in {machine}")
        else:
            logger.error(f"{self.__NAME} : FAILURE - production not added for {product} in {machine} because {reason}")
        
        return status


    # TODO : complete this function and use this for graceful thread termination
    # --------------------------------------------------------------------------
    def remmove_production() -> ERC:
        pass


    # docs
    # --------------------------------------------------------------------------
    def start(self):
        
        status = ERC.SUCCESS
        reason = ""

        logger.debug(f"{self.__NAME} : starting")
        
        if not all(self.__machines[m].start() is ERC.SUCCESS for m in self.__machines):
                status = ERC.FAILURE
                reason = f"one of more machines failed to start correctly"
        
        if status is ERC.SUCCESS:
            logger.info(f"{self.__NAME} : SUCCESS - simulation started")
        else:
            logger.critical(f"{self.__NAME} : FAILURE - simulation not started because {reason}")

        return status


    # docs
    # --------------------------------------------------------------------------
    def stop(self):
        
        status = ERC.SUCCESS
        reason = ""

        logger.debug(f"{self.__NAME} : stopping")

        if not all(self.__machines[m].stop() is ERC.SUCCESS for m in self.__machines):
            status = ERC.FAILURE
            reason = f"one or more machines failed to stop correctly"

        if status is ERC.SUCCESS:
            logger.info(f"{self.__NAME} : SUCCESS - simulation stopped")
        else:
            logger.warn(f"{self.__NAME} : WARNING - simulator no stopped properly because {reason}")

        return status   
        #return ERC.SUCCESS            # this is irrespective of shutdown outcome


    # also an alias for simulating BREAKDOWN in future maybe
    # --------------------------------------------------------------------------
    def pause(self, machine: str = "", production: str = "") -> ERC:
        status = ERC.SUCCESS
        reason = ""

        logger.debug(f"{self.__NAME} : pausing")

        # pausing specific production in specific machine if exists
        if len(machine) > 0 and len(production) > 0:
            if machine in self.__machines:
                status = self.__machines[machine].pause(production)
            else:
                status = ERC.FAILURE
                reason = f"{machine} does not exist"

        # pausing all productions in a specific machine, if exists
        elif len(machine) > 0 and len(production) <= 0:
            if machine in self.__machines:
                status = self.__machines[machine].pause()
            else:
                status = ERC.FAILURE
                reason = f"{machine} does not exist"

        # pausing all machines, if possible
        else:
            if not all(self.__machines[m].pause() is ERC.SUCCESS for m in self.__machines):
                status = ERC.FAILURE
                reason = f"one or more machine failed to pause properly"

        if status is ERC.SUCCESS:
            logger.info(f"{self.__NAME} : SUCCESS - paused production")
        else:
            logger.error(f"{self.__NAME} : FAILURE - in pausing production because {reason}")      

        return status


    # docs
    # --------------------------------------------------------------------------
    def resume(self, machine: str = "", production: str = "") -> ERC:
        status = ERC.SUCCESS
        reason = ""

        logger.debug(f"{self.__NAME} : resuming")

        # resuming specific production in specific machine, if exists
        if len(machine) > 0 and len(production) > 0:
            if machine in self.__machines:
                status = self.__machines[machine].resume(production)
            else:
                status = ERC.FAILURE
                reason = f"{machine} does not exist"

        # resuming all productions in a specific machine, if exists
        elif len(machine) > 0 and len(production) <= 0:
            if machine in self.__machines:
                status = self.__machines[machine].resume()
            else:
                status = ERC.FAILURE
                reason = f"{machine} does not exist"

        # resuming all machines, if possible
        else:
            if not all(self.__machines[m].resume() is ERC.SUCCESS for m in self.__machines):
                status = ERC.FAILURE
                reason = f"one or more machine failed to resume properly"

        if status is ERC.SUCCESS:
            logger.info(f'{self.__NAME} : SUCCESS - resumed production')
        else:
            logger.error(f'{self.__NAME} : FAILURE - in resuming production because {reason}')

        return status


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        is_running = False

        for machine in self.__machines:
            if self.__machines[machine].is_running():
                is_running = True
                break                                                           # one of the machines is running, no need to check further

        return is_running


    # docs
    # --------------------------------------------------------------------------
    def get_status(self) -> dict:
        response = SchemaFactory.get_simulation_schema()
        
        for machine in self.__machines:
            response["machine_list"].append(machine)
            response["active_machines"] += 1 if (self.__machines[machine].is_running()) else 0
        
        return response


    # docs
    # --------------------------------------------------------------------------
    def get_machine_status(self, machine_name: str) -> dict:
        if machine_name in self.__machines:
            return self.__machines[machine_name].get_status()


    # docs
    # --------------------------------------------------------------------------
    def get_production_status(self, from_machine: str, for_product: str) -> dict:
        if from_machine in self.__machines:
            return self.__machines[from_machine].get_production_status(for_product)





    # ==========================================================================
    # TODO : Docs
    # ==========================================================================
    class __Machine:

        # docs
        # ----------------------------------------------------------------------
        def __init__(self, name: str):
            self.__CLASS = "MACHINE "
            
            self.__name = name
            self.__status = PSSC.M_IDLE
            
            self.__prod_list: Dict[str, self.__Production] = {}
            logger.trace(f"{self.__CLASS} : created new machine object {self.__name}")


        # docs
        # ----------------------------------------------------------------------
        def add_production(self, product: str, cycle_time_s: int, idle_limit_s: int) -> ERC:
            status = ERC.SUCCESS
            reason = ""

            logger.trace(f"{self.__CLASS} : searching for {product} in production list of {self.__name}")
            
            if product not in self.__prod_list:
                logger.trace(f"{self.__CLASS} : {product} was not found")
                logger.debug(f"{self.__CLASS} : adding new production for {product}")
            
                self.__prod_list[product] = self.__Production(
                    product_name = product,
                    cycle_time_s = cycle_time_s,
                    idle_limit_s = idle_limit_s)
            
            else:
                logger.warn(f"{self.__CLASS} : {product} production already exists in {self.__name}")
                status = ERC.FAILURE
                reason = "Duplicate production isn't allowed."

            if status is ERC.SUCCESS:
                logger.debug(f"{self.__CLASS} : production added for {product} in {self.__name}")
            else:
                logger.error(f"{self.__CLASS} : production not added for {product} in {self.__name} because {reason}")

            return status


        # docs
        # ----------------------------------------------------------------------
        def remove_production(self, product_name: str) -> ERC:
            status = ERC.SUCCESS
            reason = ""

            # logger.debug(f"{self.__NAME} : [{self.__machine_name}] - removing production for - {product_name}")

            if product_name in self.__prod_list:
                self.__prod_list[product_name].stop()   # blocking
                self.__prod_list.pop(product_name)
            else:
                status = ERC.FAILURE
                reason = f"Production {product_name} does not exist."

            if status is ERC.SUCCESS:
                logger.debug(f"{self.__CLASS} : [{self.__name}] - production remove SUCCESS for - {product_name}")
            else:
                logger.error(f"{self.__CLASS} : [{self.__name}] - production remove FAILURE for - {product_name}")

            return status

        
        # docs
        # ----------------------------------------------------------------------
        def start(self) -> ERC:
            status = ERC.SUCCESS
            reason = ""

            logger.debug(" ")                # cosmetic separator for trace logs
            logger.debug(f"{self.__CLASS} : starting machine {self.__name}")
                
            if not all(self.__prod_list[p].start() is ERC.SUCCESS for p in self.__prod_list):
                status = ERC.FAILURE
                reason = f"on or more productions failed to start correctly"
            
            if status is ERC.SUCCESS:
                logger.info(f"{self.__CLASS} : SUCCESS - productions started on {self.__name}")
            else:
                logger.error(f"{self.__CLASS} : FAILURE - production not started on {self.__name} because {reason}")

            return status 


        # docs
        # ----------------------------------------------------------------------
        def stop(self) -> ERC:
            status = ERC.SUCCESS
            reason = ""

            # logger.debug(f"{self.__NAME} : stopping")
            for production in self.__prod_list:

                if self.__prod_list[production].stop() is not ERC.SUCCESS:
                    status = ERC.FAILURE
                    break

            if not self.is_running():
                self.__status = PSSC.M_IDLE

            if status is ERC.SUCCESS:
                logger.info(f"{self.__CLASS} : SUCCESS - productions stopped on {self.__name}")
            else:
                logger.warn(f"{self.__CLASS} : WARNING - production not stopped normally on {self.__name} because {reason}")

            return status


        # Pauses production of a process. Pauses all production if no specific
        # is given
        # ----------------------------------------------------------------------
        def pause(self, specific_prod_name: str = "") -> ERC:
            status = ERC.FAILURE
            reason = ""

            # logger.debug(f"{self.__NAME} : pausing")

            if len(specific_prod_name) == 0:
                for prod in self.__prod_list:
                    status = self.__prod_list[prod].pause()
                    if status is not ERC.SUCCESS:
                        break     # no need to try further if failed in one step

            else:
                if specific_prod_name in self.__prod_list:
                    status = self.__prod_list[specific_prod_name].pause()
                # else:
                #   status = ERC.FAILURE

            if status is ERC.SUCCESS:
                logger.debug(f"{self.__CLASS} : [{self.__name}] - production pause SUCCESS - {specific_prod_name}")
            else:
                logger.warn(f"{self.__CLASS} : [{self.__name}] - production pause FAILURE - {specific_prod_name}. {reason}")

            return status


        # Resumes production of a process. Resumes all production if no specific
        # name is given
        # ----------------------------------------------------------------------
        def resume(self, production: str = "") -> ERC:
            status = ERC.SUCCESS
            reason = ""

            if len(production) > 0:
                logger.trace(f"{self.__CLASS} : resuming {production} productions in {self.__name}")
                if production in self.__prod_list:
                    status = self.__prod_list[production].resume()
                else:
                    status = ERC.FAILURE
                    reason = f"{production} does not exist"

            else:
                logger.trace(f"{self.__CLASS} : resuming all productions in {self.__name}")
                if not all(self.__prod_list[p].resume() is ERC.SUCCESS for p in self.__prod_list):
                    status = ERC.FAILURE
                    reason = f"one or more production failed to resume properly"

            if status is ERC.SUCCESS:
                logger.debug(f"{self.__CLASS} : SUCCESS - resumed production")
            else:
                logger.error(f"{self.__CLASS} : FAILURE - in resuming production because {reason}")

            return status


        # A machine is marked as running, if at least one of its production is
        # running. If none of its production are running, the machine is marked
        # as not running. Here I default the is_running status to False, then
        # iterate over all the productions and add (OR boolean operator) them.
        # If the status changes to true, it means one of the production is runn-
        # ing. So I stop the check right there. (Complexity O(n) for worst case)
        # ----------------------------------------------------------------------
        def is_running(self) -> bool:
            return any(self.__prod_list[p].is_running() for p in self.__prod_list)


        # docs
        # ----------------------------------------------------------------------
        def get_status(self) -> dict:
            schema = SchemaFactory.get_machine_schema()

            schema["machine_name"] = self.__machine_name
            schema["machine_status"] = self.__status.value

            for each_prod in self.__prod_list:
                schema["production_list"].append(each_prod)
                schema["production_count"] += self.__prod_list[each_prod].get_status()["production_count"]

            return schema


        # Returns production status of a particular process in a machine. Sends 
        # status of all productions if no specific production name is given
        # ----------------------------------------------------------------------
        def get_production_status(self, specific_prod_name: str = "") -> dict:
            response = {}

            if len(specific_prod_name) == 0:
                for production in self.__prod_list:
                    response[production] = self.__prod_list[production].get_status()
            else:
                if specific_prod_name in self.__prod_list:
                    response = self.__prod_list[specific_prod_name].get_status()
                # else:
                #   status = ERC.FAILURE

            return response





        # ======================================================================
        # TODO : explain this class
        # ======================================================================
        class __Production:

            # docs
            # ------------------------------------------------------------------
            def __init__(self, 
                product_name: str,
                cycle_time_s: int,
                idle_limit_s: int
            ):
                self.__NAME = "PRODUXN "
                self.__product_name = product_name
                self.__cycle_time_s = cycle_time_s
                self.__idle_limit_s = idle_limit_s
                
                self.__production_amount = 0
                self.__last_cycle_time_s = 0
                self.__status   = PSSC.P_INACTIVE

                # self.__is_paused      = threading.Event()
                self.__is_waiting     = False
                self.__requested_stop = True
                self.__runtime_thread = threading.Thread(target = self.__job)

                logger.trace(f"{self.__NAME} : created new production object {self.__product_name} with cycle time - {cycle_time_s}s and idle limit - {idle_limit_s}s")


            # docs
            # ------------------------------------------------------------------
            def start(self) -> ERC:
                status = ERC.SUCCESS
                reason = ""

                logger.trace(f"{self.__NAME} : starting production for {self.__product_name}")
                
                self.__is_waiting = False
                self.__requested_stop = False
                self.__runtime_thread.start()
                time.sleep(0.1)         # waits to ensure thread loop is running

                if not self.is_running():
                    status = ERC.FAILURE
                    reason = "runtime process is not active"
                
                if status is ERC.SUCCESS:
                    logger.debug(f"{self.__NAME} : startup SUCCESS for production {self.__product_name}")
                else:
                    logger.error(f"{self.__NAME} : startup FAILURE for production {self.__product_name} because {reason}")

                return status


            # docs
            # ------------------------------------------------------------------
            def stop(self) -> ERC:
                status = ERC.SUCCESS
                reason = ""
                
                logger.trace(f"{self.__NAME} : stopping production for {self.__product_name}")

                self.__requested_stop = True
                self.__is_waiting = False           # clears existing paused processes (if any)
                self.__runtime_thread.join()        # blocking

                if self.is_running():
                    status = ERC.FAILURE
                    reason = "runtime process thread is still active"

                if status is ERC.SUCCESS:
                    logger.debug(f"{self.__NAME} : stoppage SUCCESS for production {self.__product_name}")
                else:
                    logger.error(f"{self.__NAME} : stoppage FAILURE for production {self.__product_name} because {reason}")

                return status


            # docs
            # ------------------------------------------------------------------
            def pause(self) -> ERC:
                status = ERC.FAILURE
                reason = ""

                if self.is_running():
                    status = ERC.SUCCESS
                    # logger.warn(f"{self.__NAME} : {self.__product_name}'s production can't be paused. Production not active.")
                
                if status is ERC.SUCCESS:
                    status = ERC.SUCCESS if not self.__is_waiting else ERC.FAILURE
                    # status = ERC.FAILURE if self.__is_paused.is_set() else ERC.SUCCESS
                    # logger.warn(f"{self.__NAME} : {self.__product_name}' production is already paused")

                if status is ERC.SUCCESS:
                    self.__is_waiting = True
                    # self.__is_paused.set()
                    
                if status is ERC.SUCCESS:
                    logger.debug(f"{self.__NAME} : {self.__product_name}'s production pause SUCCESS")
                else:
                    logger.warn(f"{self.__NAME} : {self.__product_name}'s production pause FAILURE. {reason}")

                return status


            # docs
            # ------------------------------------------------------------------
            def resume(self) -> ERC:
                status = ERC.FAILURE
                reason = ""

                if not self.is_running():
                    status = ERC.SUCCESS
                    # logger.warn(f"{self.__NAME} : {self.__product_name}'s production can't be resumed. Production not active.")

                if status is ERC.SUCCESS:
                    status = ERC.SUCCESS if self.__is_waiting else ERC.FAILURE
                    # status = ERC.SUCCESS if self.__is_paused.is_set() else ERC.FAILURE
                    # logger.warn(f"{self.__NAME} : {self.__product_name}' production is already running")

                if status is ERC.SUCCESS:
                    self.__is_waiting = False
                    # self.__is_paused.clear()
                   
                if status is ERC.SUCCESS:
                    logger.debug(f"{self.__NAME} : {self.__product_name}'s production resume SUCCESS")
                else:
                    logger.warn(f"{self.__NAME} : {self.__product_name}'s production resume FAILURE. {reason}")

                return status


            # The thread must be active and must not be paused to make the production
            # running
            # ------------------------------------------------------------------
            def is_running(self):
                return self.__runtime_thread.is_alive() and not self.__is_waiting # and not self.__is_paused.is_set()


            # docs
            # ------------------------------------------------------------------
            def get_status(self) -> dict:
                schema = SchemaFactory.get_production_schema()

                schema["production_name"]         = self.__product_name
                schema["production_count"]        = self.__production_amount
                schema["production_status"]       = self.__status.value
                schema["production_cycle_time_s"] = self.__cycle_time_s
                schema["production_idle_limit_s"] = self.__idle_limit_s
                schema["production_last_cycle_s"] = round(self.__last_cycle_time_s, 3)

                return schema


            # docs
            # ------------------------------------------------------------------
            def __job(self):
                while not self.__requested_stop:
                    
                    production_start = time.perf_counter()
                    self.__perform_job()
                    production_end = time.perf_counter()

                    self.__last_cycle_time_s = production_end - production_start
                    self.__evaluate_perf_status(self.__last_cycle_time_s)

                    if self.__is_waiting:
                        self.__status = PSSC.P_BREAKDOWN
                        while self.__is_waiting:
                            time.sleep(2)

                    # if self.__is_paused.is_set():
                    #    self.__status = PSSC.P_BREAKDOWN                       # PSSC.P_PAUSED     <-- I like this one
                    #    self.__is_paused.wait()                                # blocked until resumed

                # after production loop is stopped
                self.__status = PSSC.P_INACTIVE


            # docs
            # ------------------------------------------------------------------
            def __perform_job(self) -> None:
                self.__production_amount += 1
                time.sleep(random.randint(self.__cycle_time_s, self.__idle_limit_s))


            # docs
            # ------------------------------------------------------------------
            def __evaluate_perf_status(self, duration) -> None:
                
                # if manufacture time is beyond idle_limt, status = BREAKDOWN
                if duration > self.__idle_limit_s:
                    self.__status = PSSC.P_BREAKDOWN

                # else if manufacture time is more than 50% of cycle_time but
                # less than idle_limit, status = IDLE
                elif duration > self.__cycle_time_s * 1.5:
                    self.__status = PSSC.P_IDLE

                # else if machine time is more than 25% of cycle_time but less
                # than idle limit, status = SLOW
                elif duration > self.__cycle_time_s * 1.25:
                    self.__status = PSSC.P_SLOW

                # else machine is active / healthy
                else:
                    self.__status = PSSC.P_ACTIVE