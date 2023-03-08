# description for this module in 50 words
# ..



# standard imports
import argparse
import json
import logging
import os
import time
import sys

# global vars
from source.apps.pluxsim import globals

# internal imports
from source.apps import pluxsim as APP
from source.apps.pluxsim.config import Configurator
from source.apps.pluxsim.modbus.agent import Modbus_Agent
from source.apps.pluxsim.server import HTTP_Server
from source.apps.pluxsim.simulator.simulator import Simulator_T

# component imports
from source.components.io import logger
# from source.components.simulator.simulator import Simulator

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..



# ==============================================================================
# TODO : explain this class
# ==============================================================================
class Pluxsim:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self) -> None:
        self.__NAME    = 'PXSAPP  '
        self.__cfgfile = None
        self.__logdir  = None
        self.__stdout  = False
        self.__loglvl  = 2                                                      # defaults to logging.INFO

        self.__config  = Configurator()
        self.__core    = self.__Core()

        self.__requested_stop = True


    # docs
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        
        status = ERC.SUCCESS

        if status is ERC.SUCCESS:
            status = self.__process_cmdline()

        if status is ERC.SUCCESS:
            status = self.__config.parse(self.__cfgfile)

        if status is ERC.SUCCESS:
            status = self.__setup_logging(self.__config.get_app_config())

        if status is ERC.SUCCESS:
            logger.info(f"{self.__NAME} : starting {APP.NAME} v{APP.VERS}")

        if status is ERC.SUCCESS:
            status = self.__core.configure(self.__config)

        if status is ERC.SUCCESS:
            status = self.__core.start()
            self.__requested_stop = False

        if status is ERC.SUCCESS:
            logger.info(f"{self.__NAME} : running")

            while self.is_running() and not self.__requested_stop:
                time.sleep(2)

            logger.info(f"{self.__NAME} : stopping")

        if status is ERC.SUCCESS:
            status = self.__core.stop()

        if status is ERC.SUCCESS:
            status = ERC.SUCCESS if not self.is_running() else ERC.FAILURE

        logger.info(f"{self.__NAME} : stopped")
        return status


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> None:
        self.__requested_stop = True
        return ERC.SUCCESS if self.is_running() else ERC.FAILURE


    # docs
    # --------------------------------------------------------------------------
    def is_running(self) -> bool:
        return self.__core.is_running()

    # docs
    # --------------------------------------------------------------------------
    def __process_cmdline(self) -> ERC:
        
        status = ERC.SUCCESS
        parser = argparse.ArgumentParser()

        parser.add_argument("--config", type = str,
            help = 'path to json file with application configurations')
        parser.add_argument("--stdout", action = 'store_true',
            help = "whether to display logs on standard output")

        # argv[0] is the name of program and thus len(argv) is always 1
        # So, when argv[0] < 2, it means the passed cmdline input is incomplete
        if len(sys.argv) < 2:
            parser.print_help()
            status = ERC.FAILURE

        if status is ERC.SUCCESS:
            self.__cfgfile = parser.parse_args().config
            self.__stdout  = parser.parse_args().stdout

        return status


    # docs
    # --------------------------------------------------------------------------
    def __setup_logging(self, config: dict) -> ERC:
        
        status = ERC.SUCCESS
        
        log_handles = [logging.StreamHandler(sys.stdout)]
        log_format  = '%(asctime)s.%(msecs)03d [%(levelname).1s] : %(message)s'
        log_datefmt = '%Y-%m-%d %H:%M:%S'

        if config["log"]["to_file"] == True:
            log_path = config["log"]["directory"]

            if not os.path.exists(log_path):
                try: os.makedirs(log_path)
                except Exception as e:
                    print(f"log directory create FAILRE at: {self.__logdir} with error: {e}")
                    status = ERC.EXCEPTION

            log_handles.append(logging.FileHandler(f'{log_path}/{APP.NAME.lower()}.log'))

        if status == ERC.SUCCESS:
            logging.addLevelName(level = 5, levelName = "TRACE")
            logging.basicConfig(
                format   = log_format,
                datefmt  = log_datefmt,
                handlers = log_handles)
            
            match config["log"]["level"]:
                case 0: logging.getLogger().setLevel(5)    # TRACE
                case 1: logging.getLogger().setLevel(logging.DEBUG)
                case 2: logging.getLogger().setLevel(logging.INFO)
                case 3: logging.getLogger().setLevel(logging.WARN)
                case 4: logging.getLogger().setLevel(logging.ERROR)
                case 5: logging.getLogger().setLevel(logging.FATAL)
        
        return status


    # ==========================================================================
    # TODO : explain this class
    # ==========================================================================
    class __Core:

        # docs
        # ----------------------------------------------------------------------
        def __init__(self) -> None:
            self.__NAME = 'PXSCORE '
            self.__simulator = Simulator_T()
            self.__web_server = HTTP_Server()
            self.__modbus_server = Modbus_Agent()
            self.__grpc_server = None


        # docs
        # ----------------------------------------------------------------------
        def configure(self, config: Configurator) -> ERC:
            
            status = ERC.SUCCESS
            logger.debug(f"{self.__NAME} : configuring")

            if status == ERC.SUCCESS:
                status = self.__simulator.configure(config.get_simulator_config())

            if status == ERC.SUCCESS:
                status = self.__web_server.configure(
                    simulator = self.__simulator,
                    host = config.get_webserver_config()["host"]["ip"],
                    port = config.get_webserver_config()["host"]["port"])

            if status == ERC.SUCCESS:
                status = self.__modbus_server.configure(
                    config = config.get_modbus_config(),
                    simulator = self.__simulator,
                    simulator_config = config.get_simulator_config())                
            
            # ..

            if status is ERC.SUCCESS:
                logger.info(f"{self.__NAME} : configuration SUCCESS")
            else:
                logger.critical(f"{self.__NAME} : configuration FAILURE")       # critical since failure at this level prohibits the application to even start

            return status


        # docs
        # ----------------------------------------------------------------------
        def start(self) -> ERC:
            
            status = ERC.SUCCESS
            logger.debug(f"{self.__NAME} : starting")

            if status == ERC.SUCCESS:
                status = self.__simulator.start()

            if status == ERC.SUCCESS:
                status = self.__web_server.start()

            #if status == ERC.SUCCESS:
            #    status = self.__modbus_server.start()

            # ..

            if status is ERC.SUCCESS:
                logger.info(f'{self.__NAME} : start SUCCESS')
            else:
                logger.critical(f"{self.__NAME} : start FAILURE")

            return status         


        # docs
        # ----------------------------------------------------------------------
        def stop(self) -> ERC:
            
            status = ERC.SUCCESS
            logger.debug(f"{self.__NAME} : stopping")

            if status is ERC.SUCCESS:
                status = self.__web_server.stop()

            if status is ERC.SUCCESS:
                status = self.__simulator.stop()

            #if status == ERC.SUCCESS:
            #    status = self.__modbus_server.stop()

            # ..

            if status is ERC.SUCCESS:
                logger.info(f'{self.__NAME} : stop SUCCESS')
            else:
                logger.error(f"{self.__NAME} : stop FAILURE")                   # this is not critical since core is closing anyway

            return status     


        # docs
        # ----------------------------------------------------------------------
        def is_running(self) -> bool:
            return self.__web_server.is_running() or self.__simulator.is_running() 