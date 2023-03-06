# describe this module in 50 words
# ..



# standard imports
from werkzeug.serving import make_server
import json
from multiprocessing import Process
import threading
import time

# internal imports
# ..

# component imports
# ..

# shared imports
from source.shared.errorcodes.status import ERC

# thirdparty imports
import fastapi
import flask
import uvicorn



# Use this solution : https://stackoverflow.com/a/45017691
# Try this solution : https://stackoverflow.com/a/17053522
# ==============================================================================
# TODO : Docs
# ==============================================================================
class Server:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self):
        self.__NAME = "PXS-WEBSVR"
        self.__server = FastAPI()
        self.__runtime = None


    def configure(self, host: str, port: int) -> ERC:
        self.__runtime = Process(
            target = self.__job, 
            args   = [host, port])

    
    def add_route(self, path, method, callback):
        self.__server.add_api_route(
            path = path,
            methods = method,
            endpoint = callback)


    def start(self):
        self.__runtime.start()


    def stop(self):
        self.__runtime.kill()


    def is_running(self):
        return self.__runtime.is_alive()


    def __job(self, hostname, portnum):
        uvicorn.run(
            app = self.__server,
            host = hostname,
            port = portnum)
    
    
    # ==========================================================================
    # Internal runtime of HTTP server that is based on Flask. This core will be
    # run on a separate thread by the Server class
    # ==========================================================================
    class __Core:

        # docs
        # ----------------------------------------------------------------------
        def __init__(self, host: str, port: int):
            self.__hostname = host
            self.__port = port
            self.__app = Flask()

        # docs
        # ----------------------------------------------------------------------
        def start(self):
            self.__app.run(
                host = self.__hostname, 
                port = self.__port)

        # docs
        # ----------------------------------------------------------------------
        def stop(self):
            pass



# FLASK EXAMPLE
# ------------------------------------------------------------------------------
from flask import Flask

class MyServer:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route('/')
        def hello():
            return 'Hello, World!'

    def run(self):
        self.app.run()

    def close(self):
        # Use the Flask method `close` to shut down the server
        self.app.close()

server = MyServer()
server.run()

# Later on, when you want to shut down the server:
server.close()


# FASTAPI EXAMPLE
# ------------------------------------------------------------------------------
from uvicorn import run
from fastapi import FastAPI

class HTTPServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.app = FastAPI()

    def add_route(self, path: str, callback):
        self.app.route(path)(callback)

    def run(self):
        run(self.app, host=self.host, port=self.port, log_level="info", reload=True)

if __name__ == "__main__":
    server = HTTPServer("localhost", 8000)
    server.add_route("/", lambda: {"message": "Hello World"})
    server.run()


# Uvicorn Worker example
# ------------------------------------------------------------------------------
# from uvicorn import run, Config, UvicornWorker
from uvicorn.config import Config
from uvicorn.workers import UvicornWorker
from fastapi import FastAPI

class HTTPServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.worker = None

    def add_route(self, path: str, callback):
        self.app.route(path)(callback)

    def run(self):
        config = Config(app=self.app, host=self.host, port=self.port, log_level="info", reload=True)
        self.worker = UvicornWorker(config=config)
        self.worker.start()

    def stop(self):
        self.worker.stop()

if __name__ == "__main__":
    server = HTTPServer("localhost", 8000)
    server.add_route("/", lambda: {"message": "Hello World"})
    server.run()
    # Stop the server after 1 second
    sleep(1)
    server.stop()