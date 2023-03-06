# description of this module in 50 words
# ..



# standard imports
from enum import Enum

# internal imports
# ..

# component imports
# ..

# shared imports
# ..

# thirdparty imports
# ..



# ==============================================================================
# TODO : PSSC refers to PluxSimStatusCodes
# ==============================================================================
class PSSC(Enum):

    # machine operational status codes (100 - 199)
    M_IDLE      = 100
    M_RUNNING   = 101
    M_SERVICING = 102
    # ..

    # production status codes (200 - 299)
    P_INACTIVE  = 200
    P_ACTIVE    = 201
    P_SLOW      = 202
    P_PAUSED    = 203
    P_IDLE      = 204
    P_BREAKDOWN = 205