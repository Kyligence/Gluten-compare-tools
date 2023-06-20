import logging

from core.common import config
from core.common.writer import write_csv
from core.connection.mysql_client import insert_into_inconsistent_record, insert_into_response_time
from core.result.comparer import Comparer

log = config.log


def to_sorted_string(rows):
    return str(sorted([str(x) for x in rows]))


def to_sorted_trans_string(rows):
    return str(sorted(
        [str(x).replace("None", "''").replace("'NaN'", "None").replace("'-Infinity'", "None") for x in rows]))


def to_string(rows):
    return str([str(x) for x in rows])


def to_trans_string(rows):
    return str(
        [str(x).replace("None", "''").replace("'NaN'", "None").replace("'-Infinity'", "None") for x in rows])


def is_consistent(query, gluten_original_result, normal_original_result, any_exception, schema):
    if any_exception:
        return False

    if len(gluten_original_result) != len(normal_original_result):
        return False

    if len(gluten_original_result) != 0 and (len(gluten_original_result[0]) != len(normal_original_result[0])
                                             or len(schema) != len(normal_original_result[0])):
        return False

    if to_string(gluten_original_result) == to_string(normal_original_result):
        return True

    if to_sorted_string(gluten_original_result) == to_sorted_string(normal_original_result):
        return True

    gluten_result = to_sorted_trans_string(gluten_original_result)
    normal_result = to_sorted_string(normal_original_result)
    if gluten_result == normal_result:
        return True
    else:
        for row in range(0, len(normal_original_result)):
            if to_string(gluten_original_result[row]) == to_string(normal_original_result[row]):
                continue

            for col in range(0, len(schema)):
                if to_string(gluten_original_result[row][col]) == to_string(normal_original_result[row][col]):
                    continue

                if schema[col].is_float:
                    try:
                        gluten_result_float = float(gluten_original_result[row][col])
                        normal_result_float = float(normal_original_result[row][col])
                        if abs(gluten_result_float - normal_result_float) / abs(gluten_result_float) > 0.01:
                            return False
                    except ValueError:
                        return False
                else:
                    return False

    return True


class KEComparer(Comparer):
    # ConnectionManager = "ansi"
    insert_result = True

    def __init__(self):
        pass

    def compare(self, standards_results):
        gluten_result = ""
        normal_result = ""
        res_time_dict = {"gluten_res_time": 0, "normal_res_time": 0}
        if_fallback = False
        any_exception = False
        schema = None

        for i in range(0, len(standards_results.results)):

            if standards_results.results[i].exception is None:
                if standards_results.results[i].dest["tag"] == "gluten":
                    gluten_result = standards_results.results[i].content
                    if_fallback = standards_results.results[i].if_fallback
                elif standards_results.results[i].dest["tag"] == "normal":
                    normal_result = standards_results.results[i].content
                    schema = standards_results.results[i].schema
            else:
                any_exception = True
                if standards_results.results[i].dest["tag"] == "gluten":
                    gluten_result = standards_results.results[i].exception
                elif standards_results.results[i].dest["tag"] == "normal":
                    normal_result = standards_results.results[i].exception
                    return
            res_time_dict[standards_results.results[i].dest["tag"] + "_res_time"] = \
                standards_results.results[i].response_time

        consistent = is_consistent(standards_results.query["sql"], gluten_result, normal_result, any_exception, schema)

        if self.insert_result:
            if not consistent:
                insert_into_inconsistent_record(standards_results.query["project"], standards_results.query["sql"],
                                                str(gluten_result), str(normal_result))
            else:
                insert_into_response_time(standards_results.query["project"], standards_results.query["sql"],
                                          int(res_time_dict["gluten_res_time"]), int(res_time_dict["normal_res_time"]),
                                          int(if_fallback))

        return consistent
