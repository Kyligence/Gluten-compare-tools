import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import ke_config
from src.entry.response import Response, StandardResult
from src.entry.types import Types, Schema


def sort_key(query_response):
    return query_response["index"]


def do_request(index: int, url: str, body: json, header: json) -> json:
    response = requests.post(url, json=body, headers=header)
    return {"index": index, "result": json.loads(response.content.decode("utf-8"))}


def parse_schema_meta(column_metas):
    schemas: list[Schema] = []

    if column_metas is None:
        return schemas

    for i in range(0, len(column_metas)):
        column_meta = column_metas[i]
        is_float = False
        if column_meta["columnType"] == Types.FLOAT.value or column_meta["columnType"] == Types.DOUBLE.value:
            is_float = True

        schemas.append(Schema({"name": column_meta["name"], "is_float": is_float}))

    return schemas


class KE(object):

    def __init__(self, source_message):
        self.pool = ThreadPoolExecutor(max_workers=10)

        self.source_message = source_message
        js = json.loads(self.source_message)
        self.statement = re.sub("/\*\+(.)+\*/", "", js['sql'])
        self.limit = js['limit']
        self.project = js['project']
        self.header = {"Accept": "application/vnd.apache.kylin-v4+json", "Authorization": ke_config["Authorization"],
                       "Connection": "keep-alive"}

    def query(self) -> Response:
        source_message_prepared: json = {"sql": self.statement, "project": self.project, "limit": self.limit}

        urls = ke_config["urls"]
        future_list = []
        for i in range(0, len(urls)):
            future_list.append(self.pool.submit(do_request, i, urls[i], source_message_prepared, self.header))

        results = []
        for future in as_completed(future_list):
            results.append(future.result())

        return self.to_response(results)

    def to_response(self, results: list) -> Response:
        results.sort(key=sort_key)

        res = Response()
        res.source_message = self.source_message
        res.project = self.project

        for i in range(0, len(results)):
            result = results[i]["result"]
            other = StandardResult({})

            if result["code"] == "000":
                data: dict = result["data"]
                if data.get("exceptionMessage") is None and data.get("exceptionMessage") == "":
                    other.response_time = data["duration"]
                    other.time_trace = data["traces"]
                    if other.time_trace is not None:
                        for trace in other.time_trace:
                            if trace["name"] == "SPARK_JOB_EXECUTION":
                                other.spark_job_time = trace["duration"]
                                break

                    if data.get("glutenFallback") is not None:
                        other.fallback = data.get("glutenFallback")

                    res.results.append(data["results"])
                    res.schema = parse_schema_meta(data["columnMetas"])
                else:
                    other.exception = data.get("exceptionMessage")
                    res.exception = True
                    res.results.append(None)
            else:
                other.exception = result["exception"]
                other.stacktrace = result["stacktrace"]

                res.exception = True
                res.results.append(None)

            res.others.append(other)

        return res

    def to_readable(self) -> str:
        return self.project + "|" + self.statement
