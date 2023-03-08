# This configurator module provides a minimal interface to any application that
# wishes to use json or json5 format files for its configuration settings. This
# module can parse the json configuration file and stores their memory represen
# tation as a dictionary which can then be used as necessary. It is advised to
# use this module as a base class for creating a configurator instead of editing
# its functionality directly.

# standard imports
import enum
import json
import os
import tomllib

# sibling imports
# ..

# thirdparty imports
import json5



# docs
# ==============================================================================
class Configurator:

    # internal enumerated list that for execution status codes
    # --------------------------------------------------------------------------
    class __ERC(enum.Enum):
        SUCCESS = 0
        FAILURE = 1
        FILE_NOT_FOUND = 2
        INVALID_FILE_TYPE = 3
        PARSING_EXCEPTION = 4


    # basic constructor
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__config_object: dict = None

    
    # basic desctructor
    # --------------------------------------------------------------------------
    def __del__(self):
        self.__config_object = None

    
    # docs
    # --------------------------------------------------------------------------
    def _parse_config(self, file_path : str) -> int:
        status = self.__ERC.SUCCESS

        if not os.path.exists(file_path):
            status = self.__ERC.FAILURE

        if status == self.__ERC.SUCCESS:
            try:
                if file_path.lower().endswith(('json', 'json5', 'jsonc')):
                    self.__config_object = json5.load(open(file_path))
                elif file_path.lower().endswith('toml'): 
                    self.__config_object = tomllib.load(open(file_path, mode = "rb"))
                else:
                    status == self.__ERC.INVALID_FILE_TYPE

            except Exception as e:
                print(e)
                status = self.__ERC.PARSING_EXCEPTION

        return status.value


    # docs
    # --------------------------------------------------------------------------
    def _get_config_object(self) -> dict | None:
        return self.__config_object


    # docs
    # --------------------------------------------------------------------------
    def _get_value(self, key:str) -> any:
        if self.__config_object is not None:
            if key in self.__config_object:
                return self.__config_object[key]   
        return None