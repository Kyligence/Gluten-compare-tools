import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from core.common import config
from core.message.request_builder import RequestBuilder

log = config.log


def query(url: json, body: str, header: str) -> json:
    response = requests.post(url["url"], json=body, headers=header)
    return {"dest_url": url, "result": json.loads(response.content.decode("utf-8"))}


class KERequestBuilder(RequestBuilder):
    pool = ThreadPoolExecutor(max_workers=10)

    def __init__(self):
        super().__init__()

    def parse_source(self, source_message):
        parsed_sql = re.sub("/\*\+(.)+\*/", "", source_message['sql'])
        return {"sql": parsed_sql, "project": source_message['project']}

    def build_forward_message(self, source_message_parsed):
        addition = {"Accept": "application/vnd.apache.kylin-v4+json", "Authorization": "Basic QURNSU46S1lMSU4=",
                    "Connection": "keep-alive"}
        return source_message_parsed, addition

    # @retry(stop_max_attempt_number=10, wait_fixed=1000 * 2 * 60)
    def send(self, urls, source_message_prepared, addition):
        results = {"source_message": source_message_prepared, "addition": addition, "results": []}
        future_list = []

        for i in range(0, len(urls)):
            future_list.append(self.pool.submit(query, urls[i], source_message_prepared, addition))

        for future in as_completed(future_list):
            results["results"].append(future.result())

        return results
