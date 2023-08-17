import os
import json
import random

from locust import TaskSet, task, between
from locust import FastHttpUser

from config import csv_config
from src.database.reader import CsvReader
from src.entry.csv_format import CsvFormat
from src.entry.response import GoreplayReceive


class KETaskSet(TaskSet):

    def __init__(self, parent: "User"):
        super().__init__(parent)
        self.headers = None

    def on_start(self):
        print("start")
        self.headers = {
            "Accept": "application/vnd.apache.kylin-v4+json", "Authorization": "Basic QURNSU46S1lMSU4=",
            "Connection": "keep-alive", "Content-Type": "application/json;charset=UTF-8"
        }

    @task(1)
    def query(self):
        payload = json.loads(random.choice(RequestsArr))
        # payload = {"sql": "select 1", "project": "hltest"}

        response = self.client.post("/kylin/api/query", json=payload, headers=self.headers, verify=False)
        if response.status_code != 200:
            print(response.text)
        assert response.status_code == 200


class MyLocust(FastHttpUser):
    tasks = [KETaskSet]
    wait_time = between(1, 2)


def add_row_to_arr(value: CsvFormat):
    RequestsArr.append(value.to_redis_format())


RequestsArr = []
# reader = CsvReader("/home/admin123/PycharmProjects/compareTools/test")
reader = CsvReader(csv_config["pt_source_parent_dir"])

result = GoreplayReceive()
reader.read_to_other(csv_config["pt_source_file"], result, add_row_to_arr)

if __name__ == '__main__':
    import os

    # os.system("locust -f locust_pt.py --host=http://127.0.0.1:7070")
    os.system(
        "locust -f locust_pt.py --headless -u 20 -r 5 -t 20s --host=http://127.0.0.1:7070 --csv=pt_results/2023-07-19/example"
    )


