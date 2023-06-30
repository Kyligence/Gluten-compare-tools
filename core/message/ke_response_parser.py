from core.message.response_parser import ResponseParser, StandardResults, StandardResult, Schema

from src.entry.types import Types


def parse_schema_meta(column_metas):
    schemas = []

    if column_metas is None:
        return schemas

    for i in range(0, len(column_metas)):
        column_meta = column_metas[i]
        is_float = False
        if column_meta["columnType"] == Types.FLOAT.value or column_meta["columnType"] == Types.DOUBLE.value:
            is_float = True

        schemas.append(Schema(column_meta["name"], is_float))

    return schemas


class KEResponseParser(ResponseParser):
    # ConnectionManager = "ansi"

    def __init__(self):
        pass

    def parse_dest_response(self, results):
        standard_results = StandardResults()
        standard_results.query = results["source_message"]
        standard_results.addition = results["addition"]
        for i in range(0, len(results["results"])):
            result_dict = results["results"][i]["result"]
            standard_result = StandardResult()
            standard_result.dest = results["results"][i]["dest_url"]
            standard_result.code = result_dict["code"]

            if standard_result.code == "000":
                standard_result.response_time = result_dict["data"]["duration"]  # to do
                standard_result.content = result_dict["data"]["results"]
                standard_result.exception = result_dict["data"]["exceptionMessage"]
                if standard_result.dest["tag"] == "gluten":
                    standard_result.if_fallback = result_dict["data"]["glutenFallback"]

                standard_result.schema = parse_schema_meta(result_dict["data"]["columnMetas"])
            else:
                standard_result.response_time = -1
                standard_result.content = None
                standard_result.exception = result_dict["exception"]

            standard_results.results.append(standard_result)

        return standard_results

#     @retry(stop_max_attempt_number=10, wait_fixed=1000 * 2 * 60)
#     def send(self, urls, source_message_prepared, addition):
#         results = {"source_message": source_message_prepared, "addition": addition, "results": []}
#         for i in range(0, len(urls)):
#             # log.log(i, urls[i])
#             # cal time here??
#             response = requests.post(urls[i]["url"], json=source_message_prepared, headers=addition)
#             result_json = response.content.decode("utf-8")
#             results["results"].append({"dest_url": urls[i], "result.py": json.loads(result_json)})
#
#         return results
#
# DEST_URLS = [
#     {"tag": "gluten", "url": "http://127.0.0.1:8190/kylin/api/query"},  # ke+gluten,
#     {"tag": "normal", "url": "http://127.0.0.1:8191/kylin/api/query"},  # ke+vanilla spark
# ]
