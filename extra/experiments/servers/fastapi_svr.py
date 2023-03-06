# REFER TO THIS PLEASE https://stackoverflow.com/a/67908797
# USING THE DESIGN MENTIONED HERE https://stackoverflow.com/a/70563827
# ==============================================================================
# TODO : explain this class
# ==============================================================================
class Server_FastAPI:

    # docs
    # --------------------------------------------------------------------------
    def __init__(self) -> None:
        self.__NAME    = 'PLUXSIM-SERV'
        self.__stdout  = True
        self.__verbose = True

        self.__core   = self.__Core()
        self.__config = None
        self.__server_runtime = threading.Thread(target=self.__runtime, args=[self.__config])

        self.__is_running = False
        self.__requested_stop = True


    # docs
    # --------------------------------------------------------------------------
    def configure(self, config: Configurator) -> None:
        self.__config = config


    # docs
    # --------------------------------------------------------------------------
    def start(self) -> None:
        if self.__is_running:
            self.stop()

            self.__requested_stop = False
            self.__server_runtime.start()
            self.__is_running = self.__server_runtime.is_alive()


    # docs
    # --------------------------------------------------------------------------
    def stop(self, force: True) -> None:
        if self.__is_running:
            self.__server_runtime.join()        # this is blocking :(


    # docs
    # --------------------------------------------------------------------------
    def __runtime(self, config: Configurator):
        uvicorn.run(
            app    = self.__core, 
            host   = "0.0.0.0", # config.get_host_ip(), 
            port   = 8080, # config.get_host_port(),
            reload = True)


    # ==========================================================================
    # TODO : explain this class
    # ==========================================================================
    class __Core:
        
        # docs
        # ----------------------------------------------------------------------
        def __init__(self):
            self.__app = FastAPI()

            self.__app.add_api_route(
                path     = "/",
                methods  = ["GET"],
                endpoint = self.__api_index)

            self.__app.add_api_route(
                path     = "/health",
                methods  = ["GET"],
                endpoint = self.__api_get_health)
        
        
        # docs
        # ----------------------------------------------------------------------
        async def __api_index(self):
            return {"message": "Hello"}


        # docs
        # ----------------------------------------------------------------------
        async def __api_get_health(self):
            return {"status" : "Healthy"}


'''
# https://stackoverflow.com/a/64521239

class UviServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()

config = uvicorn.Config("example:app", host="127.0.0.1", port=5000, log_level="info")
server = Server(config=config)

with server.run_in_thread():
    # Server is started.
    ...
    # Server will be stopped once code put here is completed
    ...

# Server stopped.
'''