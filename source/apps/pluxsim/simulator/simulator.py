# description of this module in 50 words
# ..



#standard imports
from typing import Dict

# internal imports
from source.apps.pluxsim.simulator.internal.machine import Machine
from source.apps.pluxsim.simulator.internal.machine import Machine_T

# component imports
from source.components.io import logger

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..



# ==============================================================================
#  TODO : explain class
# ==============================================================================
class Simulator:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__CNAME = "PXSIM   "
        self.__machines: Dict[str, Machine] = {}

    # A simulator is only responsible for adding a production to machine that
    # exists, it doesn't handles whether the production is duplicate or not.
    # That is the job of the machine itself, the machine will tell the simulator
    # "Hey, I already have this production in me. What to do now?"
    # This removes duplication of efforts and makes the codebase more leaner.
    # --------------------------------------------------------------------------
    def add_production(self, 
            for_product, 
            machine, 
            with_cycle_time_s, 
            and_breakdown_theshold_s,
            having_breakdown_pct
        ) -> ERC:

        if machine not in self.__machines:
            self.__machines[machine] = Machine(machine)

        status = self.__machines.get(machine).add_production(
            for_product, with_cycle_time_s, and_breakdown_theshold_s, having_breakdown_pct)

        if status is not ERC.SUCCESS:
            logger.error(f"{self.__CNAME} : FAILURE - production not added {for_product} in {machine} because [{status.name}]")
        
        return status    
    
    # docs
    # --------------------------------------------------------------------------
    def remove_production(self, for_product, in_machine) -> ERC:
        pass
    
    # starts all the machines and their most recently added production
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        if all(machine.start_production() is ERC.SUCCESS for machine in self.__machines.values()):
            return ERC.SUCCESS
        return ERC.FAILURE

    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        if all(machine.stop_production() is ERC.SUCCESS for machine in self.__machines.values()):
            return ERC.SUCCESS
        return ERC.FAILURE

    # docs
    # --------------------------------------------------------------------------
    def resume(self, in_machine, for_product = "") -> ERC:
        status = ERC.FAILURE

        # resume specific production in specific machine, if exists
        if len(for_product) > 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                status = self.__machines.get(in_machine).resume_production(for_product)
            else:
                status = ERC.MACHINE_NOT_FOUND

        # resume all productions in a specific machine, if exists
        elif len(for_product) <= 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                status = self.__machines.get(in_machine).resume_production()
            else:
                status = ERC.MACHINE_NOT_FOUND

        # resume all machines, that are paused
        else:
            if not all(machine.resume_production() is ERC.SUCCESS for machine in self.__machines.values()):
                status = ERC.FAILURE

        return status

    # docs
    # --------------------------------------------------------------------------
    def pause(self, in_machine, for_product = "") -> ERC:
        status = ERC.FAILURE

        # pause specific production in specific machine, if exists
        if len(for_product) > 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                status = self.__machines.get(in_machine).pause_production(for_product)
            else:
                status = ERC.MACHINE_NOT_FOUND

        # pause all productions in a specific machine, if exists
        elif len(for_product) <= 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                status = self.__machines.get(in_machine).pause_production()
            else:
                status = ERC.MACHINE_NOT_FOUND

        # pause all machines, that are active
        else:
            if not all(machine.pause_production() is ERC.SUCCESS for machine in self.__machines.values()):
                status = ERC.FAILURE

        return status

    # is true if atleast one of the machine is running atleast one production
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return any(machine.is_running() for machine in self.__machines.values())

    # docs
    # --------------------------------------------------------------------------
    def get_status(self, for_product = "", in_machine = "") -> dict:
        
        # default schema for simulator
        response = { "machines" : [] }

        # get status of a specific production from a specific machine
        if len(for_product) > 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                response = self.__machines.get(in_machine).get_status(for_product)

        # get status of a specific machine
        elif len(for_product) <= 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                response = self.__machines.get(in_machine).get_status()

        # get status of all machines (i.e, the simulator)
        else:
            for machine in self.__machines.values():
                response["machines"].append(machine.get_status())

        return response

    # docs
    # --------------------------------------------------------------------------
    def switch_production(self, to_product, in_machine) -> ERC:
        if in_machine in self.__machines:
            return self.__machines[in_machine].switch_production(to_product)
        else:
            return ERC.MACHINE_NOT_FOUND




class Simulator_T:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__CNAME = "PXSIM   "
        self.__machines : Dict[str, Machine_T] = {}

    
    # docs
    # --------------------------------------------------------------------------
    def add_machine(self, name: str, breakdown_pct: float, products: dict = {}) -> ERC:
        
        status = ERC.MACHINE_ALREADY_EXISTS if name in self.__machines else ERC.SUCCESS

        if status is ERC.SUCCESS:
            status = ERC.PRODUCTION_NOT_FOUND if len(products) <= 0 else ERC.SUCCESS

        if status is ERC.SUCCESS:
            self.__machines[name] = Machine_T(name, breakdown_pct)
            status = ERC.SUCCESS if name in self.__machines else ERC.MEMORY_ALLOC_FAILURE

        if status is ERC.SUCCESS:
            try:
                for product in products:
                    status = self.__machines.get(name).add_product(
                        product["name"],
                        product["cycle_time_s"],
                        product["breakdown_threshold_s"])

                    if status is not ERC.SUCCESS:
                        raise RuntimeError(f"exception while adding product for {product['name']} with code {status.value} [{status.name}]")

            except Exception as e:
                logger.error(f"{self.__CNAME} : FAILURE - production not added in {name} because {e}")
                return ERC.EXCEPTION

        if status is not ERC.SUCCESS:
            logger.error(f"{self.__CNAME} : FAILURE - add machine failed with code {status.value} [{status.name}]")
        
        return status

    
    # docs
    # --------------------------------------------------------------------------
    def remove_machine(self) -> ERC:
        pass


    # docs
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        if all(machine.start() is ERC.SUCCESS for machine in self.__machines.values()):
            return ERC.SUCCESS
        return ERC.FAILURE


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        if all(machine.stop() is ERC.SUCCESS for machine in self.__machines.values()):
            return ERC.SUCCESS
        return ERC.FAILURE


    # docs
    # --------------------------------------------------------------------------
    def resume(self, machine = "") -> ERC:
        status = ERC.FAILURE

        # resume a machine, if exists
        if len(machine) > 0:
            if machine in self.__machines:
                status = self.__machines.get(machine).resume()
            else:
                status = ERC.MACHINE_NOT_FOUND

        # resume all machines, that are paused
        else:
            if not all(machine.resume() is ERC.SUCCESS for machine in self.__machines.values()):
                status = ERC.FAILURE

        return status


    # docs
    # --------------------------------------------------------------------------
    def pause(self, machine = "") -> ERC:
        status = ERC.FAILURE

        # pause a machine, if exists
        if len(machine) > 0:
            if machine in self.__machines:
                status = self.__machines.get(machine).pause()
            else:
                status = ERC.MACHINE_NOT_FOUND

        # pause all machines, that are running
        else:
            if not all(machine.pause() is ERC.SUCCESS for machine in self.__machines.values()):
                status = ERC.FAILURE

        return status


    # is true if atleast one machine is running
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return any(machine.is_running() for machine in self.__machines.values())

    
    # docs
    # --------------------------------------------------------------------------
    def get_status(self, for_product = "", in_machine = "") -> dict:

        # default schema for simulator
        response = { "machines" : [] }

        # get status of a specific production from a specific machine
        if len(for_product) > 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                response = self.__machines.get(in_machine).get_status(for_product)

        # get status of a specific machine
        elif len(for_product) <= 0 and len(in_machine) > 0:
            if in_machine in self.__machines:
                response = self.__machines.get(in_machine).get_status()

        # get status of all machines (i.e., the simulator)
        else:
            for machine in self.__machines.values():
                response["machines"].append(machine.get_status())

        return response


    # docs
    # --------------------------------------------------------------------------
    def switch_production(self, to_product, in_machine) -> ERC:
        if in_machine in self.__machines:
            return self.__machines.get(in_machine).switch(to_product)
        else:
            return ERC.MACHINE_NOT_FOUND