# standard imports
import argparse
import asyncio
import copy
import json
import logging
import multiprocessing
import threading
import time

# component imports
from source.components.io import logger
from source.apps.pluxsim.simulator.simulator import Simulator_T

# shared imports
from source.shared.errorcodes.status import ERC

# third party imports
import httpx
from pymodbus.server.async_io import ModbusTcpServer, ModbusSocketFramer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification




# ------------------------------------------------------------------------------
# docs
# ------------------------------------------------------------------------------
class Configurator:
    def __init__(self, conf_data: dict):
        self.__data = conf_data
        # TODO : Add data validation call here, throw exception (since we are
        # inside constructor) and handle it afterwards :)

    def get_host(self) -> tuple:
        return (self.__data["host"]["ip"], self.__data["host"]["port"])
    
    def get_co(self) -> dict:
        return self.__data["register"]["co"]
    
    def get_di(self) -> dict:
        return self.__data["register"]["di"]
    
    def get_hr(self) -> dict:
        return self.__data["register"]["hr"]
    
    def get_ir(self) -> dict:
        return self.__data["register"]["ir"]
    
    def get_id(self):
        return self.__data["id"]
    


# ==============================================================================
# The following class is a simple definition for the Modbus Server Agent that
# will run on the main thread. It has a separate data syncing facility over HTTP
# ==============================================================================
class Modbus_Async_Client:
    
    # docs
    # --------------------------------------------------------------------------
    def __init__(self, config: Configurator):
        
        self.__CNAME = "AGENT    : [Modbus] "
        self.__config: Configurator = config

        # Using ModbusSlaveContext class to manage the data blocks that are used
        # to store the values of all the registes
        self.__slave_registers = ModbusSlaveContext(

            # The first arg in ModbusSequentialDataBlock specifies the starting
            # address of the data block and the second argument list * size,
            # creates a data block with reg_count number of registers starting
            # at address 0, each with value of 0
            #
            # A data block is a list of registers where each register can store
            # 16 bit integer value. And these values are provided in a python
            # list format. So, the syntax
            # ModbusSequentialDataBlock(0x0, [0,1,2,3,4])
            # means that a data block with 5 registers having value 0,1,2,3 and
            # 4 is created
            #
            # So I use the following python shorthand for creating a list of
            # specified length with all values set to 0. The general format is
            # ModbusSequentialDataBlock(start_address, [init_val] * registers_count)
            #
            # Direct Input register available by function code 1                        
            di = ModbusSequentialDataBlock(
                address = self.__config.get_di()["addr"],
                values  = [0] * self.__config.get_di()["size"]),
            
            # Coil register, available by function code 2
            co = ModbusSequentialDataBlock(
                address = self.__config.get_co()["addr"],
                values  = [0] * self.__config.get_co()["size"]),

            
            # Holding Register, available by function code 3
            hr = ModbusSequentialDataBlock(
                address = self.__config.get_hr()["addr"], 
                values  = [0] * self.__config.get_hr()["size"]),

            
            # Input Register, available by function code 4
            ir = ModbusSequentialDataBlock(
                address = self.__config.get_ir()["addr"], 
                values  = [0] * self.__config.get_ir()["size"])
        )

        # Using ModbusServerContext class to manage the context of all connected
        # slaves
        self.__context = ModbusServerContext(
            slaves = self.__slave_registers, 
            single = True)
        
        # Set device identification
        self.__id = ModbusDeviceIdentification()
        self.__id.ProductName = self.__config.get_id()["product"]["name"]
        self.__id.ProductCode = self.__config.get_id()["product"]["code"]
        self.__id.ModelName   = self.__config.get_id()["product"]["model"]
        self.__id.VendorName  = self.__config.get_id()["vendor"]["name"]
        self.__id.VendorUrl   = self.__config.get_id()["vendor"]["url"]
        self.__id.MajorMinorRevision = self.__config.get_id()["product"]["version"]


    # docs
    # --------------------------------------------------------------------------
    async def start(self):
        self.__server = ModbusTcpServer(
            context = self.__context,
            framer  = ModbusSocketFramer,
            identity= self.__id,
            address = self.__config.get_host())
        
        logger.debug(f"{self.__CNAME} : starting")
        await self.__server.serve_forever()         # blocking
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    async def stop(self):
        logger.debug(f"{self.__CNAME} : stopping")
        await self.__server.shutdown()
        await self.__server.server_close()
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def update_register(self, fc, addr, values) -> ERC:
        self.__slave_registers.setValues(fc, addr, values)
    


# This class wraps the internal async Modbus Agent class and gives us a clean
# synchronized and usable interface to work with
# ------------------------------------------------------------------------------
class Modbus_Service:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__CNAME = "SERVICE  : [Modbus] "
        self.__agent: Modbus_Async_Client = None
        # self.__agent_thread = threading.Thread(target = self._async_routines)
        self.__agent_thread = multiprocessing.Process(target = self._async_routines)
        self.__data_sync = threading.Thread(target = self.__data_updater)
        self.__is_requested_stop = True

        # HACK : Turns off logging from asyncio library, using selector: EpollSelector
        import logging
        logging.getLogger('asyncio').setLevel(logging.WARNING)


    # docs
    # --------------------------------------------------------------------------
    def configure(self, config, simulator: Simulator_T, simulator_config: dict) -> ERC:

        self.__simulator_ref = simulator
        self.__machines_config = simulator_config["machine"]
        self.__config = Configurator(config)

        self.__agent = Modbus_Async_Client(self.__config)
        return ERC.SUCCESS
    

    # docs
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        logger.debug(f"{self.__CNAME} : starting")
        
        self.__is_requested_stop = False
        self.__agent_thread.start()
        time.sleep(2)

        self.__data_sync.start()

        logger.info(f"{self.__CNAME} : start SUCCESS")
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        logger.debug(f"{self.__CNAME} : stopping")
        
        self.__is_requested_stop = True
        self.__data_sync.join()
        # self.__agent.stop()
        self.__agent_thread.terminate()

        logger.info(f"{self.__CNAME} : stop SUCCESS")
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> ERC:
        return self.__data_sync.is_alive()


    # docs
    # --------------------------------------------------------------------------
    def _async_routines(self):
        asyncio.run(self.__agent.start())         # blocking

    # The following code is beyond stupid. It contains little bit of hacks and
    # patchworks. Will be improved in upcoming stable builds.
    # --------------------------------------------------------------------------
    def __data_updater(self) -> None:

        # machine -> modbus.hr map
        map_info = {
            "machine" : "",
            "reg_type": "hr",
            "lsw_at"  : 0,
            "msw_at"  : 0,
        }
        mappings = []

        # parse machine config to decode mappings
        for machine in self.__machines_config:
            map = copy.deepcopy(map_info)
            map["machine"] = machine
            map["lsw_at"]  = self.__machines_config[machine]["modbus"]["hr"]["lsw"]
            map["msw_at"]  = self.__machines_config[machine]["modbus"]["hr"]["msw"]
            mappings.append(map)
        
        # create generic registers to store values
        co_reg = [0] * self.__config.get_co()["size"]
        di_reg = [0] * self.__config.get_di()["size"]
        hr_reg = [0] * self.__config.get_hr()["size"]
        ir_reg = [0] * self.__config.get_ir()["size"]
        
        # get into a loop that refers to simulator and updates data every second
        while not self.__is_requested_stop:
            
            for map in mappings:
                production = self.__simulator_ref.get_status(in_machine = map["machine"])["total_production"]
                hr_reg[map["msw_at"]] = divmod(production, 0x10000)[0]
                hr_reg[map["lsw_at"]] = divmod(production, 0x10000)[1]
                self.__agent.update_register(0x3, 0x0, hr_reg)

            time.sleep(1)