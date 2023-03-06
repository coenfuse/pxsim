# This module contains routing function definitions for various HTTP requests



# standard imports
from http import server
from http.server import BaseHTTPRequestHandler
import json

# internal imports
# ..

# component imports
from source.components.simulator.simulator import Simulator

# shared imports
# ..

# thirdparty imports
# ..



# docs
# ------------------------------------------------------------------------------
def get_status(simulator: Simulator) -> str:
    return json.dumps(simulator.get_status()).encode()

# docs
# ------------------------------------------------------------------------------
def get_machine_status(simulator: Simulator, machine_name: str) -> str:
    return json.dumps(simulator.get_machine_status(machine_name)).encode()

# docs
# ------------------------------------------------------------------------------
def get_production_status(simulator: Simulator, machine_name: str, production: str) -> str:
    return json.dumps(simulator.get_production_status(machine_name, production)).encode()