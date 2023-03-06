# This is the only working example since it is using asyncio.
# Had to spend days thanks to depreciated documentation and 3 years old stack
# overflow threads. Almost cried here.
# The following code works with pymodbus 3.12, requires redis and sqlachemy pip
# installs as well.

import asyncio
from pymodbus.server.async_io import ModbusTcpServer, ModbusSocketFramer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


async def run_server():
    store = ModbusSlaveContext(
        ir=ModbusSequentialDataBlock(30001, [152, 276]), 
        zero_mode=True)

    context = ModbusServerContext(slaves=store, single=True)
    server  = ModbusTcpServer(context, ModbusSocketFramer, address=("localhost",5020))
    
    print("Server starting")
    await server.serve_forever()                              # this is blocking

if __name__ == "__main__":
    asyncio.run(run_server())

