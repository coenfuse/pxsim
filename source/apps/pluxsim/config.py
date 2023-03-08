# A configurator class for Pluxsim application that provides the codebase a sim-
# ple access to the configuration files globally. It contains all the data vali-
# dation checks and error handling for the config parameters here itself. Uses 
# config shared package as a base class and supports configurations of format 
# json and json5 only.



# standard imports
# ..

# internal imports
# ..

# component imports
from source.components.io import logger

# shared imports
from source.shared.config.configurator import Configurator as __BaseConfigurator
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..



# docs
# ==============================================================================
class Configurator(__BaseConfigurator):

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__NAME = 'CONFIG  '


    # docs
    # --------------------------------------------------------------------------
    def parse(self, config_file_path: str) -> ERC:
        match super()._parse_config(config_file_path):
            case 0 : return ERC.SUCCESS
            case 1 : return ERC.FAILURE
            case 2 : return ERC.FAILURE
            case 3 : return ERC.FAILURE
            case 4 : return ERC.EXCEPTION
        

    # docs
    # --------------------------------------------------------------------------
    def __inspect(self):
        print(f"{self.__NAME} : inspecting")
        
        config_obj = super()._get_config_object()
        for key in config_obj:
            if key != 'production_jobs':                                        # because of insane log tree
                print(f"{self.__NAME} : using {key} = {config_obj[key]}")
        
        print(f"{self.__NAME} : inspect SUCCESS")
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def get_app_config(self) -> int:
        return super()._get_value("pxsim")
    
    # docs
    # --------------------------------------------------------------------------
    def get_webserver_config(self) -> int:
        return super()._get_value("http")

    # docs
    # --------------------------------------------------------------------------
    def get_modbus_config(self) -> int:
        return super()._get_value("modbus")
    
    # docs
    # --------------------------------------------------------------------------
    def get_simulator_config(self) -> int:
        return super()._get_value("simulator")
    
    # ..