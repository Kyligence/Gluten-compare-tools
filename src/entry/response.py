import json
from json import JSONEncoder
from typing import List

from src.entry.csv_format import CsvFormat
from src.entry.types import Schema, SchemaEncoder


def json_list_to_standard_result(srs: List[dict]):
    arr = []
    for sr in srs:
        arr.append(StandardResult(sr))

    return arr


class StandardResult(object):
    def __init__(self, dic: dict):
        if dic.get("response_time") is None:
            self.response_time = 0
        else:
            self.response_time = dic.get("response_time")

        if dic.get("exception") is None:
            self.exception = ""
        else:
            self.exception = dic.get("exception")

        if dic.get("stacktrace") is None:
            self.stacktrace = ""
        else:
            self.stacktrace = dic.get("stacktrace")

        if dic.get("fallback") is not None:
            if str(dic.get("fallback")).lower() == "true":
                self.fallback = True
            else:
                self.fallback = False
        else:
            self.fallback = False

        if dic.get("time_trace") is None:
            self.time_trace = []
        else:
            self.time_trace = dic.get("time_trace")

        if dic.get("spark_job_time") is None:
            self.spark_job_time = 0
        else:
            self.spark_job_time = dic.get("spark_job_time")


class StandardResultEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Response(CsvFormat):

    def __init__(self):
        super().__init__()
        self.project: str = ""
        self.source_message: str = ""
        self.schema: List[Schema] = []
        self.results: list = []
        self.others: List[StandardResult] = []
        self.exception: bool = False
        self.diff_time: float = 0

    def to_csv_format(self):
        return [self.project, self.source_message, json.dumps(self.schema, cls=SchemaEncoder), json.dumps(self.results),
                json.dumps(self.others, cls=StandardResultEncoder),
                self.exception, self.diff_time]

    def from_csv_format(self, row: list):
        self.project = row[0]
        self.source_message = row[1]
        self.schema = json.loads(row[2], object_hook=Schema)
        self.results = json.loads(row[3])
        self.others = json_list_to_standard_result(json.loads(row[4]))

        if row[5] == "True":
            self.exception = True
        else:
            self.exception = False

            if len(self.others) == 2 and self.others[0].response_time is not None \
                    and self.others[0].response_time != 0 \
                    and self.others[1].response_time is not None:
                self.diff_time = (self.others[0].response_time - self.others[1].response_time) \
                                 / self.others[0].response_time


class GoreplayReceive(CsvFormat):
    message: str

    def __init__(self):
        super().__init__()
        self.message = ""

    def to_csv_format(self):
        return [self.message]

    def from_csv_format(self, row: list):
        self.message = row[0]

    def to_redis_format(self):
        return self.message
