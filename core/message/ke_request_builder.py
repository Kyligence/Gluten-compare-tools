import json

from core.common import config
from core.message.request_builder import RequestBuilder
import requests
from retrying import retry

log = config.log


# pip install retrying

class KERequestBuilder(RequestBuilder):

    def __init__(self):
        pass

    def parse_source(self, source_message):
        return source_message

    def build_forward_message(self, source_message_parsed):
        addition = {"Accept": "application/vnd.apache.kylin-v4+json", "Authorization": "Basic QURNSU46S1lMSU4=",
                    "Connection": "keep-alive", "Accept": "application/vnd.apache.kylin-v4+json"}
        return source_message_parsed, addition

    # @retry(stop_max_attempt_number=10, wait_fixed=1000 * 2 * 60)
    def send(self, urls, source_message_prepared, addition):
        results = {"source_message": source_message_prepared, "addition": addition, "results": []}
        for i in range(0, len(urls)):
            # log.log(i, urls[i])
            # cal time here??
            response = requests.post(urls[i]["url"], json=source_message_prepared, headers=addition)
            result_json = response.content.decode("utf-8")
            results["results"].append({"dest_url": urls[i], "result": json.loads(result_json)})

        return results

# DEST_URLS = [
#     {"tag": "gluten", "url": "http://127.0.0.1:8190/kylin/api/query"},  # ke+gluten,
#     {"tag": "normal", "url": "http://127.0.0.1:8191/kylin/api/query"},  # ke+vanilla spark
# ]