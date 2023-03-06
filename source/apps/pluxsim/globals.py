# this module contains global variables that are accessed throughout the Pluxsim
# project. Highly undesirable due to variable being global. But can't find a better
# alternative to having reference / pointer to a same variable across different
# modules.

# standard imports
# ..

# dependency imports
from source.apps.pluxsim.simulator.simulator import Simulator_T
# from source.components.simulator.simulator import Simulator
from source.components.io.controller import KeyboardController
from source.apps.pluxsim.server import HTTP_Server

# ------------------------------------------------------------------------------
# Global reference for the pluxsimulator
g_PLUXSIM: Simulator_T = None

# Global reference for the webserver
g_HTTPSERVER: HTTP_Server = None

# Global reference for the KeyboardController
g_CINCTRL: KeyboardController = None