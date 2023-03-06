import httpx
import json
import threading
import time

# third party imports
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class PXC:
    
    # docs
    # --------------------------------------------------------------------------
    def __init__(self, pxs_url: str, ifx_url: str, ifx_org: str, ifx_key: str):
        
        self.__ifx_cli = influxdb_client.InfluxDBClient(url = ifx_url, token = ifx_key, org = ifx_org)
        self.__ifx_writer = self.__ifx_cli.write_api(write_options = SYNCHRONOUS)
        self.__ifx_reader = self.__ifx_cli.query_api()

        self.__pxs_root = pxs_url
        self.__req_stop = True
        self.__jobs_t = []
        self.__read_t = []


    # docs
    # --------------------------------------------------------------------------
    def add_job(self, machine: str, product: str, bucket: str, interval_s: int):
        self.__jobs_t.append(threading.Thread(
            target= self.__job, 
            args  = [machine, product, bucket, interval_s],
            name  = f"plxc-for-prod-{product}"))


    # docs
    # --------------------------------------------------------------------------
    def add_query(self, query_name: str, query: str, interval_s: int):
        self.__read_t.append(threading.Thread(
            target = self.__reader,
            args   = [query_name, query, interval_s],
            name   = f"plxc-query-{query_name}"))

    # docs
    # --------------------------------------------------------------------------
    def remove_job(self):
        pass


    # docs
    # --------------------------------------------------------------------------
    def start(self):
        print("Starting ...")
        self.__req_stop = False
        for each_job in self.__jobs_t:
            each_job.start()

        for each_reader in self.__read_t:
            each_reader.start()


    # docs
    # --------------------------------------------------------------------------
    def stop(self):
        print("Stopping ...")
        self.__req_stop = True
        for each_job in self.__jobs_t:
            each_job.join()                                           # blocking

        for each_reader in self.__read_t:
            each_reader.join()                                        # blocking


    # docs
    # --------------------------------------------------------------------------
    def __job(self, machine: str, product: str, bucket: str, interval_s: int):
        while not self.__req_stop:

            # retrieve data from http
            parameter = {"machine" : machine, "product": product}
            response  = httpx.get(f"{self.__pxs_root}/status", params= parameter)
            response  = json.loads(response.text)

            # stage write data
            prod_amount = int(response["total_production"])
            prod_time   = int(response["last_production_duration_s"]) 
            
            # create data string for influx entry
            entry = influxdb_client.Point(machine).tag("product", product).field("amount", prod_amount).field("last_prod_time", prod_time)

            # try to write data into influxdb
            try:
                self.__ifx_writer.write(bucket, record=entry)
            except Exception as e:
                print(f"Error writing data to influxdb with exception {e}")

            # wait before next http poll request
            time.sleep(interval_s)


    # docs
    # --------------------------------------------------------------------------
    def __reader(self, query_name: str, query: str, interval_s: int):
        while not self.__req_stop:
            
            # tables = self.__ifx_reader.query(query, org="felidae")
            # for table in tables:
            #    for record in table.records:
            #        print(record)

            time.sleep(interval_s)




# ==============================================================================
# ACTION STARTS HERE
# ==============================================================================
if __name__ == "__main__":
    
    ifx_token = "e-LP2KzC3swrSFExvzlfA2skY5Y2sl33JIzXCFrzGViou3RzZJO0r2f-XhY1-j4VscNqzj-ZtXjrAe_nzGErSw=="

    app = PXC(
        pxs_url = "http://127.0.0.1:11204",      # mention url where pluxsim instance is serving simulation data
        ifx_url = "http://localhost:8086",      # mention url where the influxdb instance is hosted
        ifx_org = "felidae",                    # mention the name of influxdb organization that is housing your data bucket
        ifx_key = ifx_token)                    # mention the db access key / token

    app.add_job(
        machine = "fruitninja",
        product = "apple",
        bucket  = "sample",
        interval_s = 5)

    app.add_job(
        machine = "fruitninja",
        product = "kiwi",
        bucket  = "sample",
        interval_s = 3)

    app.add_job(
        machine = "fruitninja",
        product = "orange",
        bucket  = "sample",
        interval_s = 5)

    app.add_job(
        machine = "fruitninja",
        product = "papaya",
        bucket  = "sample",
        interval_s = 1)

    app.add_job(
        machine = "fruitninja",
        product = "peach",
        bucket  = "sample",
        interval_s = 6)

    app.add_job(
        machine = "auto",
        product = "audi",
        bucket  = "sample",
        interval_s = 70)

    app.add_job(
        machine = "auto",
        product = "hyundai",
        bucket  = "sample",
        interval_s = 32)

    app.add_job(
        machine = "auto",
        product = "maruti",
        bucket  = "sample",
        interval_s = 24)

    app.add_job(
        machine = "auto",
        product = "pagani",
        bucket  = "sample",
        interval_s = 90)

    app.add_job(
        machine = "auto",
        product = "tata",
        bucket  = "sample",
        interval_s = 21)

    app.add_job(
        machine = "grofers",
        product = "bhindi",
        bucket  = "sample",
        interval_s = 5)

    app.add_job(
        machine = "grofers",
        product = "cauliflower",
        bucket  = "sample",
        interval_s = 2)

    app.add_job(
        machine = "grofers",
        product = "onion",
        bucket  = "sample",
        interval_s = 4)

    app.add_job(
        machine = "grofers",
        product = "potato",
        bucket  = "sample",
        interval_s = 2)

    app.add_job(
        machine = "grofers",
        product = "tomato",
        bucket  = "sample",
        interval_s = 3)

    app.add_job(
        machine = "nerolac",
        product = "bianca",
        bucket  = "sample",
        interval_s = 8)

    app.add_job(
        machine = "nerolac",
        product = "giallo",
        bucket  = "sample",
        interval_s = 5)

    app.add_job(
        machine = "nerolac",
        product = "nero",
        bucket  = "sample",
        interval_s = 2)

    app.add_job(
        machine = "nerolac",
        product = "rosa",
        bucket  = "sample",
        interval_s = 18)

    app.add_job(
        machine = "nerolac",
        product = "verde",
        bucket  = "sample",
        interval_s = 17)

    app.add_query(
        query_name = "minute_agtr",
        interval_s = 15,
        query = '''
from(bucket:"pluxdb")
|> range(start: -1h)
|> filter(fn: (r) => r["_measurement"] == "fruitninja")
|> filter(fn: (r) => r["Production"] == "peach")
|> filter(fn: (r) => r["_field"] == "prod_time")
|> aggregateWindow(every: 5m, fn: mean)
|> yield(name: "hourly")
        '''
    )

    app.start()
    input("Press enter to terminate ...\n\n")
    app.stop()