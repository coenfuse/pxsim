from pymodbus.client.sync_diag import ModbusTcpClient as ModbusClient
import time

cli = ModbusClient('localhost', port=55124)
assert cli.connect()
try:
    while True:
        res = cli.read_holding_registers(0, count = 10, slave = 3)
        # assert not res.isError()
        print(res.registers)
        time.sleep(3)
except KeyboardInterrupt as e:
    print(f"Closing modbus client with keyboard interrupt {e}")