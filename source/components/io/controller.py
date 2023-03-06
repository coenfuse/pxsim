# A input controller class for Pluxsim application that provides the codebase a 
# simple access to user input and action mapping.



# standard imports
import threading
import time

# internal imports
from source.components.io import logger

# component imports
# ..

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..


# ==============================================================================
# TODO : explain this class
# ==============================================================================
class KeyboardController:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self) -> None:
        self.__NAME    = 'CINCTRL'
        self.__stdout  = True                                                   # console log input of mapped keypresses
        self.__verbose = True                                                   # console log input of unmapped keypresses

        self.__keymaps = {}                                                     # key:str, action:function    
        self.__listener_freq_ms = 100
        
        self.__listener = threading.Thread(
            target=self.__listening_job, 
            args=[self.__listener_freq_ms])

        self.__requested_stop = True


    # docs
    # --------------------------------------------------------------------------
    def add_keymap(self, key:str, action) -> None:
        pass


    # docs
    # --------------------------------------------------------------------------
    def remove_keymap(self, key:str, action) -> None:
        pass


    # docs
    # --------------------------------------------------------------------------
    def start(self, freq_ms:int) -> None:
        pass


    # docs
    # --------------------------------------------------------------------------
    def stop(self, force:True) -> None:
        self.__requested_stop = True
        self.__listener.join()


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return self.__listener.is_alive()


    # docs
    # --------------------------------------------------------------------------
    def __listening_job(self, freq_ms:int):
        while not self.__requested_stop:
            keypress = input()
            if keypress in self.__keymaps:
                self.__keymaps[keypress]
                time.sleep(freq_ms)