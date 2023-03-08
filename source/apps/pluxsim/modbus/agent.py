# description of this module in 50 words
# ..


# standard imports
import asyncio
from multiprocessing import Process
from threading import Thread
import time

# local imports
from source.apps.pluxsim.simulator.simulator import Simulator_T

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore import ModbusSlaveContext
from pymodbus.server import ModbusTcpServer
# from pymodbus.server import StartTcpServer, ServerStop
from pymodbus.framer import rtu_framer

from pymodbus.server.async_io import ModbusTcpServer
from pymodbus.framer.socket_framer import ModbusSocketFramer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext



# ------------------------------------------------------------------------------
# docs
# ------------------------------------------------------------------------------
class Configurator:
    def __init__(self, conf_data: dict):
        self.__data = conf_data

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
# TODO : docs
# ==============================================================================
class Modbus_Agent:
    
    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__NAME = "MODBUS  "
        self.__is_requested_stop = True
        
        self.__config = None
        self.__simulator_ref = None
        self.__machines_conf = None
        self.__server = None

        self.__slave_registers = None
        self.__server_runtime: Process = None
        self.__data_sync_service: Thread = None


    # docs
    # --------------------------------------------------------------------------
    def configure(self, config, simulator, simulator_config) -> ERC:

        self.__simulator_ref = simulator
        self.__machines_conf = simulator_config
        self.__config = Configurator(config)

        # Using ModbusSlaveContext class to manage the data blocks that are used
        # to store the values of all the registers
        self.__slave_registers = ModbusSlaveContext(

            # The first arg in ModbusSequentialDataBlock specifies the starting
            # address of the data block and the second argument list * size,
            # creates a data block with reg_count number of registers starting
            # at address 0, each with value of 0.
            # 
            # A data block is a list of registers where each register can store
            # 16 bit integer values. And these values are provided in a python
            # list format. So, the syntax
            # ModbusSequentialDataBlock(0x0, [0,1,2,3,4])
            # means that a data block with 5 registers having value 0,1,2,3 and 
            # 4 is created.
            # 
            # So I use the following python shorthand for creating a list of
            # specified length with all values set to 0. The general format is,
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
        context = ModbusServerContext(
            slaves = self.__slave_registers,
            single = True)

        # Set device identification, intialization will be improved later
        identity = ModbusDeviceIdentification()
        identity.ProductName = self.__config.get_id()["product"]["name"]
        identity.ProductCode = self.__config.get_id()["product"]["code"]
        identity.ModelName   = self.__config.get_id()["product"]["model"]
        identity.MajorMinorRevision = self.__config.get_id()["product"]["version"]
        identity.VendorName  = self.__config.get_id()["vendor"]["name"]
        identity.VendorUrl   = self.__config.get_id()["vendor"]["url"]

        self.__server = ModbusTcpServer(context, ModbusSocketFramer, identity, self.__config.get_host())
        self.__data_sync_service = Thread(target = self.__data_syncronizer)
        # self.__server_runtime = Process(target = asyncio.run, args = self.__server_run())
        
        return ERC.SUCCESS


    # Now any modbus client (master device) that is on the same network and is 
    # using Modbus protocol can read values from the holding registers. The cli-
    # ent would need to know the IP address and port of the server, as well as 
    # the function code (here 3 is for holding registers block) and the starting 
    # address of the holding registers. With this information, the client can 
    # send a request to server (slave device) and the slave will respond with 
    # the values stored in the requested registers block.
    #
    # I am not sure how to handle this warning, i'm stupid with asyncio
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        self.__is_requested_stop = False
        asyncio.run(self.__server_run())
        self.__data_sync_service.start()
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        self.__is_requested_stop = True
        self.__data_sync_service.join()
        asyncio.run(self.__server_stop())
        return ERC.SUCCESS


    # wrapper for asyncio compatible server runtimes.
    # the server's serve_forever() is a coroutine function. Thus, it needs to be
    # awaited for its completion and must be wrapped inside an async function.
    # That is why this definition is required
    # --------------------------------------------------------------------------
    async def __server_run(self):
        await self.__server.serve_forever()

    # wrapper ...
    # --------------------------------------------------------------------------
    async def __server_stop(self):
        await asyncio.gather(self.__server.server_close(), self.__server.shutdown())


    # docs
    # --------------------------------------------------------------------------
    def __data_syncronizer(self):
        while not self.__is_requested_stop:
            time.sleep(2)
















class Modbus_Agent_T:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__NAME = "MODBUS  "
        
        self.__sim_obj: Simulator_T = None
        self.__machines_conf: dict  = None
        
        self.__server = None
        self.__server_runtime = None

        self.__registers_count = 0
        self.__register_block: list = None

        self.__data_sync_service = Thread(target = self.__data_sync_job)
        self.__is_requested_stop = True

    # docs
    # --------------------------------------------------------------------------
    def configure(self, simulator, machines_conf, host, port, reg_count) -> ERC:
        self.__sim_obj = simulator
        self.__machines_conf = machines_conf

        self.__registers_count = reg_count
        self.__register_block   = ModbusSequentialDataBlock(0x00, [0] * reg_count)         # initializes a data block containing reg_count number of register initialzied with value 0
        slaves  = { 0x00: ModbusSlaveContext(hr = self.__register_block)}
        context = ModbusServerContext(slaves, single = True)
        identiy = None

        self.__server = ModbusTcpServer(
            context = context, 
            framer = rtu_framer, 
            identity = identiy,
            address = f"{host}:{port}")

        self.__server_runtime = Thread(target = self.__server.serve_forever)

        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        self.__is_requested_stop = False
        self.__data_sync_service.start()
        self.__server_runtime.start()
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        self.__is_requested_stop = True
        self.__server.shutdown()
        # ServerStop()
        self.__server_runtime.join(timeout = 5)
        self.__data_sync_service.join(timeout = 4)
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return True if self.__server_runtime.is_alive() and self.__data_sync_service.is_alive() and self.__is_requested_stop else False


    # The following funciton is going to be improved once I get some time with
    # better decoupling and desing choices. First idea is to have a reference
    # of an in-memory database, instead of the simulator itself.
    # --------------------------------------------------------------------------
    def __data_sync_job(self):
        while not self.__is_requested_stop:

            for machine_config in self.__machines_conf:
                for product_config in machine_config["products"]:
                    status = self.__sim_obj.get_status(
                        for_product = product_config["name"],
                        in_machine  = machine_config["name"])
                    
                    # check whether the mentioned register allocated addresses for
                    # each product falls in a valid range or not. All the indexes
                    # must be less than the total registers count
                    # if all(index < self.__registers_count for index in product_config['modbus_register_allocs']):
                        # self.__register_block[product_config['modbus_register_allocs'][0]] = status['total_production']
                        # self.__register_block[product_config['modbus_register_allocs'][1]] = status['last_production_duration_s']

            time.sleep(1)