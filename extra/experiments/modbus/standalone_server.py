# standard imports
import argparse
import asyncio
import json
import logging
import threading
import time

# third party imports
import httpx
from pymodbus.server.async_io import ModbusTcpServer, ModbusSocketFramer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification



# ==============================================================================
# The following class is a simple definition for the Modbus Server Agent that
# will run on the main thread. It has a separate data syncing facility over HTTP
# ==============================================================================
class Modbus_Agent:
    
    # docs
    # --------------------------------------------------------------------------
    def __init__(self, 
        hosting_endpoint, 
        register_config, 
        identity_config, 
        simulator_endpoint, 
        simulator_config):

        self.__hosting_address: tuple = hosting_endpoint
        self.__identity_config: dict  = identity_config
        self.__register_config: dict  = register_config

        self.__simulator_address: tuple = simulator_endpoint
        self.__simulator_configs: dict  = simulator_config

        self.__slave_registers  = None
        self.__data_sync_worker = threading.Thread(target = self.__data_sync_job)
        self.__is_requested_stop= True

        logging.getLogger().setLevel(logging.DEBUG)


    # docs
    # --------------------------------------------------------------------------
    async def start(self):
        # Using ModbusSlaveContext class to manage the data blocks that are used
        # to store the values of all the registers
        self.__slave_registers = ModbusSlaveContext(

            # The first arg in ModbusSequentialDataBlock specifies the starting
            # address of the data block. The second argument specifies the values
            # we want to put in this data block. 
            # A data block is a list of registers where each register can store
            # 16 bit integer values. And these values are provides in a python
            # list format. So if we wrote 
            # ModbusSequentialDataBlock(0x0, [0,1,2,3,4])
            # This means, I created a data block with 5 registers having values
            # 1,2,3,4 and 5.
            # 
            # In the following syntax, I've used the python shorthand for creating
            # a list of specified length with all values set to 0.
            # The general format is,
            # register = ModbusSequentialDataBlock(starting_address, [init_value] * register_count)
            di = ModbusSequentialDataBlock(self.__register_config["di"]["start_address"], [0] * self.__register_config["di"]["reg_count"]),    # accessible by func code 1, discrete input registers
            co = ModbusSequentialDataBlock(self.__register_config["co"]["start_address"], [0] * self.__register_config["co"]["reg_count"]),    # accessible by func code 2, coil registers
            hr = ModbusSequentialDataBlock(self.__register_config["hr"]["start_address"], [0] * self.__register_config["hr"]["reg_count"]),    # accessible by func code 3, holding registers
            ir = ModbusSequentialDataBlock(self.__register_config["ir"]["start_address"], [0] * self.__register_config["ir"]["reg_count"]))    # accessible by func code 4, input registers

        # Using ModbusServerContext class to manage the context of all connected
        # slaves
        context = ModbusServerContext(
            slaves = self.__slave_registers,
            single = True)

        # Set device identification, initialization will be improved later
        identity = ModbusDeviceIdentification()
        identity.VendorName         = self.__identity_config["vendor_name"]
        identity.ProductCode        = self.__identity_config["product_code"]
        identity.VendorUrl          = self.__identity_config["vendor_url"]
        identity.ProductName        = self.__identity_config["product_name"]
        identity.ModelName          = self.__identity_config["model_name"]
        identity.MajorMinorRevision = self.__identity_config["version"]

        server = ModbusTcpServer(
            context  = context, 
            framer   = ModbusSocketFramer, 
            identity = identity, 
            address  = self.__hosting_address)

        self.__is_requested_stop = False
        self.__data_sync_worker.start()    
        await server.serve_forever()       # blocking call


    # The following function reads simulated data from the simulator over HTTP 
    # (will be replaced by gRPC later) and updates the register blocks so that 
    # anytime a modbus master requests data. It will get a new one.
    # --------------------------------------------------------------------------
    def __data_sync_job(self):
        
        # initialize an empty register block
        values = [0] * self.__register_config["hr"]["reg_count"]
        while not self.__is_requested_stop:

            # update the whole register block with production data
            for machine in self.__simulator_configs.keys():
                for product in self.__simulator_configs[machine]:
                    try:                        

                        # retrieve data from http
                        url = f"http://{self.__simulator_address[0]}:{self.__simulator_address[1]}"
                        response = httpx.get(f"{url}/status", params={"machine":machine, "product":product})
                        status   = json.loads(response.text)
                    
                        # stage write data
                        prod_amount = int(status["total_production"])
                        prod_time   = float(status["last_production_duration_s"])

                        # update the register block at appropriate index for this product
                        values[self.__simulator_configs[machine][product]["register_alloc"][0]] = prod_amount
                        values[self.__simulator_configs[machine][product]["register_alloc"][1]] = prod_time

                    except Exception as e:
                        print(f"Failed to update status for {product} in machine {machine} because {e}")


            # update the slave register block with new values
            print(values)
            self.__slave_registers.setValues(
                fc_as_hex = 0x3,                # function code for the register, 3 is for holding registers
                address   = 0x0,                # starting address of register block
                values    = values)             # list of register values to assign

            # sleep before requesting for updated status again
            time.sleep(3)

    
    # docs
    # --------------------------------------------------------------------------
    def stop(self):
        self.__is_requested_stop = True



# BYTES, FERRARA and ACTION
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    hosting_address = ("0.0.0.0", 55124)

    register_config = {
        "di":{ "start_address": 0x0, "reg_count": 5 },
        "co":{ "start_address": 0x0, "reg_count": 5 },
        "hr":{ "start_address": 0x0, "reg_count": 10 },
        "ir":{ "start_address": 0x0, "reg_count": 5 }}

    identity_config = {
        "vendor_name" : "Power Profit",
        "product_code": "px_sim",
        "vendor_url"  : "",
        "product_name": "PluxSim",
        "model_name"  : "Pluxsim Modbus Slave",
        "version"     : "0.1.0" }

    simulator_address = ("localhost", 11204)
    simulator_config  = {
        "fruitninja" : {
            #"apple"  : { "register_alloc": [0,1] },         # in HR index 0 will contain prod_amount, index 1 will contain last prod time for apple
            #"kiwi"   : { "register_alloc": [2,3] },         # in HR index 2 will contain prod_amount, index 3 will contain last prod time for kiwi
            #"orange" : { "register_alloc": [4,5] },         # in HR index 4 will contain prod_amount, index 5 will contain last prod time for orange
            #"papaya" : { "register_alloc": [6,7] },         # in HR index 6 will contain prod_amount, index 7 will contain last prod time for papaya
            "peach"  : { "register_alloc": [8,9] }          # in HR index 8 will contain prod_amount, index 9 will contain last prod time for peach
        }
    }
    
    app = Modbus_Agent(hosting_address, register_config, identity_config, simulator_address, simulator_config)
    
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt as e:
        app.stop()
        print(f"Closing modbus server with keyboard interrupt {e}")