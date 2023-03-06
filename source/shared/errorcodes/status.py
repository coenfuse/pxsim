# description in 50 words
# ..

# standard imports
from enum import Enum

# thirdparty imports
# ..



# ==============================================================================
# docs : explain this class
# ==============================================================================
class ERC(Enum):

     REASON = ""

     # Basic error codes
     SUCCESS = 0
     # WARNING = 1
     FAILURE = 1
     EXCEPTION = 2
     MEMORY_ALLOC_FAILURE = 3
     THREAD_ALLOC_FAILURE = 4

     # TODO : The following will be replaced with a simple extensible ERC solution
     # Simulator ERCs
     MACHINE_ALREADY_EXISTS = 6
     MACHINE_NOT_FOUND = 7
     MACHINE_FAILED_TO_START = 8
     MACHINE_FAILED_TO_STOP = 9
     MACHINE_FAILED_TO_RESUME = 10
     MACHINE_FAILED_TO_PAUSE = 11

     PRODUCTION_ALREADY_EXISTS = 12
     PRODUCTION_NOT_FOUND = 13
     PRODUCTION_FAILED_TO_START = 14
     PRODUCTION_FAILED_TO_STOP = 15
     PRODUCTION_FAILED_TO_RESUME = 16
     PRODUCTION_FAILED_TO_PAUSE = 17 