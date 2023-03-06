# description of this project in 50 words
# ..



# standard imports
import logging
import signal

# shared imports
from source.shared.errorcodes.status import ERC

# app imports
# import source.apps.plux as APP
import source.apps.pluxsim as APP
from source.apps.pluxsim.main import Pluxsim



# ------------------------------------------------------------------------------
# TODO : explain what's going on
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    status = ERC.SUCCESS
    app    = Pluxsim()

    def sgn_handlers(signum, frame):
        if signum == signal.SIGINT:
            logging.info(f'received interrupt SIGINT [{signum}]')
            app.stop()

    signal.signal(signal.SIGINT, sgn_handlers)

    try:
        print("\n")
        status = app.start()

    except Exception as e:
        logging.error(e)
        status = ERC.EXCEPTION

    finally:
        print(f'\n{APP.NAME} exited with code {status.value} [{status.name}]')