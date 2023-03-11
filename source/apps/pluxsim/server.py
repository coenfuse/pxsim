# A HTTP webserver class for Pluxsim application that provides the codebase a 
# simple interface for creating a server.



# standard imports
from source.apps import pluxsim as APP
from source.apps.pluxsim import globals
from enum import Enum
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json
import threading
import urllib.parse as urlhelper

# internal imports
from source.apps.pluxsim.config import Configurator
from source.apps.pluxsim.simulator.simulator import Simulator
# from source.components.simulator.simulator import Simulator

# component imports
from source.components.io import logger

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
# ..


# ==============================================================================
# TODO : explain this class
# ==============================================================================
class HTTP_Server:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__NAME = "HTTPSVR "
        self.__host = "0.0.0.0"
        self.__port = 11204
        self.__server  = None
        self.__runtime = threading.Thread(target = self.__job)

        # Earlier I initialzed a server instance here on self.__server whic was
        # then followed by self.__server.serve_forever in self.__runtime target.
        # This worked well in practice and on windows. But on a deployment in
        # production using Docker, this won't work.
        # It is weird to explain since I myself do not have complete understanding
        # but initializing a server instance with a default host:port kind of
        # reserves that host:port pair and that particular server instance on the
        # network. So later on when configure the server to some other host:port
        # it doesn't work and respond to network requests. Thus I had to create
        # a new separate function call __job() that handle the initializion and
        # running of server in one block post-configuration. And it is working,
        # normally.


    # docs
    # --------------------------------------------------------------------------
    def configure(self, 
            simulator: Simulator, 
            host = "0.0.0.0", 
            port = 11204
        ) -> ERC:
        
        globals.g_PLUXSIM = simulator
        self.__host = host
        self.__port = port
        return ERC.SUCCESS


    # docs
    # --------------------------------------------------------------------------
    def start(self) -> ERC:
        if self.is_running():
            logger.info(f"{self.__NAME} : re-starting")
            self.stop()

        # logger.info(f"{self.__NAME} : starting")
        self.__runtime.start()
        
        if self.__runtime.is_alive():
            logger.info(f"{self.__NAME} : SUCCESS - listening for requests on http://{self.__host}:{self.__port}/")
            return ERC.SUCCESS
        else:
            logger.error(f"{self.__NAME} : FAILURE - not listening for requests on http://{self.__host}:{self.__port}/")
            return ERC.FAILURE


    # docs
    # --------------------------------------------------------------------------
    def stop(self) -> ERC:
        # logger.info(f"{self.__NAME} : stopping")
        self.__server.shutdown()                                                # unblocks self.__job thread
        self.__runtime.join()

        if not self.is_running():
            logger.info(f"{self.__NAME} : SUCCESS - disposed listener on http://{self.__host}:{self.__port}/")
            return ERC.SUCCESS
        else:
            logger.error(f"{self.__NAME} : FAILURE - in disposing listener on http://{self.__host}:{self.__port}/")
            return ERC.FAILURE


    # docs
    # --------------------------------------------------------------------------
    def is_running(self):
        return self.__runtime.is_alive()


    # PATCH for server not running in a Docker container
    # --------------------------------------------------------------------------
    def __job(self):
        self.__server = HTTPServer((self.__host, self.__port), self.__Router)
        self.__server.serve_forever(poll_interval = 1)                          # thread blocks here


    # ==========================================================================
    # TODO : explain the class
    # ==========================================================================
    class __Router(BaseHTTPRequestHandler):
        
        # docs
        # ----------------------------------------------------------------------
        def log_message(self, format: str, *args: any) -> None:
            request_type     = args[0].split(' ')[0]                            # splitting the str by ' ' and taking 1st item
            request_endpoint = args[0].split(' ')[1]                            # ... taking the 2nd item
            response_code    = args[1]

            if int(response_code) < 400:
                logger.debug(f"HTTPAPI : [{response_code}] - [{request_type}]{request_endpoint}")
            else:
                logger.error(f"HTTPAPI : [{response_code}] - [{request_type}]{request_endpoint}")


        # docs
        # ----------------------------------------------------------------------
        def log_error(self, format: str, *args: any) -> None:
            pass

        
        # docs
        # ----------------------------------------------------------------------
        def do_GET(self):

            # docs
            # ------------------------------------------------------------------
            def handle_json_response(response: dict):
                if response["code"] < 400:
                    self.send_response(response["code"])
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(response["body"].encode())
                else:
                    self.send_error(response["code"], response["body"], response["explain"])

            # localhost:8080/status?machine=<>&prod=<>
            # ------------------------------------------------------------------
            if self.path.startswith("/status"):
                handle_json_response(self.__get_sim_status(self.path))

            # docs
            # ------------------------------------------------------------------
            elif self.path.startswith("/pause"):
                handle_json_response(self.__get_sim_pause(self.path))

            # docs
            # ------------------------------------------------------------------
            elif self.path.startswith("/resume"):
                handle_json_response(self.__get_sim_resume(self.path))

            # docs
            # ------------------------------------------------------------------
            elif self.path.startswith("/switch"):
                handle_json_response(self.__get_sim_switch(self.path))
            # ..


            # docs
            # ------------------------------------------------------------------
            elif self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"{APP.NAME} v{APP.VERS} running".encode())

            # docs
            # ------------------------------------------------------------------
            else:
                self.send_error(
                    code    = 404, 
                    message = "NOT FOUND",
                    explain = f"Server can't find the requested resource {self.path}")


        # ======================================================================
        # HTTP ENDPOINT COMPONENTS
        # 
        # https://www.example.com:443/blog/article/search?docid=100&hl=en#dayone
        # https://             <- scheme
        # www.                 <- subdomain
        # example.             <- domain
        # com                  <- top level domain
        # :443                 <- port number
        # /blog/article/search <- path
        # ?                    <- query block separator
        # docid=100&hl=en      <- query string
        # #dayone              <- fragment
        # ======================================================================

        # docs
        # ----------------------------------------------------------------------
        def __retrieve_query_params(self, query_raw:str):
            query_dict = {}
            for query in query_raw.split('&'):
                query_dict[query.split('=')[0]] = query.split('=')[1]
            return query_dict

        # docs
        # ----------------------------------------------------------------------
        def __get_sim_status(self, request_raw: str) -> dict:
            request  = urlhelper.urlparse(request_raw)
            response = {
                "code" : 400, 
                "body" : 'Bad request',
                "explain" : ''}
            
            # check for query block, if present. Process.
            if len(request.query) != 0:
                queries = self.__retrieve_query_params(request.query)
                
                # process if 'machine' and 'product' both are queried
                if "machine" in queries and "product" in queries:
                    response_str = json.dumps(globals.g_PLUXSIM.get_status(queries['product'], queries['machine']))
                    response["body"] = response_str
                    response["code"] = 404 if len(response_str) == 0 else 200
                 
                # process if only 'machine' is queried and not 'product'
                elif "machine" in queries and not "product" in queries:
                    response_str = json.dumps(globals.g_PLUXSIM.get_status(in_machine = queries['machine']))
                    response["body"] = response_str
                    response["code"] = 404 if len(response_str) == 0 else 200
                
                # handle all the rest cases
                else:
                    response["explain"] = 'The server cannot process the provided queries'
            
            # handle general /status request
            else:
                response["body"] = json.dumps(globals.g_PLUXSIM.get_status())
                response["code"] = 200

            # finally
            return response


        # docs
        # ----------------------------------------------------------------------
        def __get_sim_pause(self, request_raw: str) -> str:
            request  = urlhelper.urlparse(request_raw)
            response = {
                "code" : 400, 
                "body" : 'Bad request',
                "explain" : ''}
            
            # check for query block, if present. Process.
            if len(request.query) != 0:
                queries = self.__retrieve_query_params(request.query)
                
                # process if the key 'machine' is present in query, i.e: pause?machine=
                if "machine" in queries:
                    if globals.g_PLUXSIM.pause(machine = queries['machine']) is ERC.SUCCESS:
                        response["body"] = "SUCCESS"                            # Consider this to be returned as serialized JSON
                        response["code"] = 200
                    else:
                        response["explain"] = f'Failed to pause machine {queries["machine"]}'
                        response["body"] = "Internal Server Error"              # The serialized json may cost more bandwidth, but it is more readable
                        response["code"] = 500
                
                # handle all the rest cases (incomplete queries and other nonsense)
                else:
                    response["explain"] = f'The server cannot process the provided query: {queries}'
            
            # handle general / pause request (pause whole simulator)
            else:
                if globals.g_PLUXSIM.pause() is ERC.SUCCESS:
                    response["body"] = 'SUCCESS'
                    response["code"] = 200
                else:
                    response["explain"] = 'Failed to pause production simulator'
                    response["body"] = 'Internal Server Error'
                    response["code"] = 500
                    
            # finally
            return response


        # docs
        # ----------------------------------------------------------------------
        def __get_sim_resume(self, request_raw: str) -> str:
            request  = urlhelper.urlparse(request_raw)
            response = {
                "code" : 400, 
                "body" : 'cannot process',
                "explain" : ''}
            
            # check for query block, if present. Process.
            if len(request.query) != 0:
                queries = self.__retrieve_query_params(request.query)
                
                # process if the key 'machine' is present in the query, i.e: resume?machine=
                if "machine" in queries:
                    if globals.g_PLUXSIM.resume(machine = queries['machine']) is ERC.SUCCESS:
                        response["body"] = "SUCCESS"                            # Consider this to be a serialized json instead
                        response["code"] = 200
                    else:
                        response["explain"] = f'Failed to resume production for {queries["product"]}'
                        response["body"] = "Internal Server Error"
                        response["code"] = 500
                
                # handle all the rest cases (incomplete queries and other nonsense)
                else:
                    response["explain"] = f'The server cannot process the provided query: {queries}'
            
            # handle general /resume request (resume whole simulator)
            else:
                if globals.g_PLUXSIM.resume() is ERC.SUCCESS:
                    response["body"] = 'SUCCESS'
                    response["code"] = 200
                else:
                    response["explain"] = 'Failed to resume production simulator'
                    response["body"] = 'Internal Server Error'
                    response["code"] = 500
                    
            # finally
            return response


        # docs
        # ----------------------------------------------------------------------
        def __get_sim_switch(self, request_raw: str) -> str:
            request  = urlhelper.urlparse(request_raw)
            response = {
                "code" : 400, 
                "body" : 'cannot process',
                "explain" : ''}

            # finally
            return response