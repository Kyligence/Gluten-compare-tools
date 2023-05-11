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


def is_consistent(query, gluten_original_result, normal_original_result, any_exception):
    if any_exception:
        return False

    if str(gluten_original_result) == str(normal_original_result):
        return True

    if query.lower().find("order by") == -1:
        gluten_result = to_sorted_trans_string(gluten_original_result)
        normal_result = to_sorted_string(normal_original_result)
        if gluten_result == normal_result:
            return True
        elif len(gluten_original_result) == 1 and len(gluten_original_result[0]) == 1:
            # find the first different column value and check out if is precision problem
            # process the simplest case here for zen,only one row and one column result
            try:
                gluten_result_float = float(gluten_original_result[0][0])
                normal_result_float = float(normal_original_result[0][0])
                if abs(gluten_result_float-normal_result_float)/abs(gluten_result_float) < 0.0001:
                    return True
                else:
                    return False
            except ValueError:
                return False
        else:
            return False
    else:
        return to_trans_string(gluten_original_result) == to_string(normal_original_result)


class KEComparer(Comparer):
    # ConnectionManager = "ansi"

    def __init__(self):
        pass

    def compare(self, standards_results):
        gluten_result = ""
        normal_result = ""
        res_time_dict = {"gluten_res_time": 0, "normal_res_time": 0}

        any_exception = False

        for i in range(0, len(standards_results.results)):

            if standards_results.results[i].exception is None:
                if standards_results.results[i].dest["tag"] == "gluten":
                    gluten_result = standards_results.results[i].content
                elif standards_results.results[i].dest["tag"] == "normal":
                    normal_result = standards_results.results[i].content
            else:
                any_exception = True
                if standards_results.results[i].dest["tag"] == "gluten":
                    gluten_result = standards_results.results[i].exception
                elif standards_results.results[i].dest["tag"] == "normal":
                    normal_result = standards_results.results[i].exception
            res_time_dict[standards_results.results[i].dest["tag"] + "_res_time"] = \
                standards_results.results[i].response_time

        if not is_consistent(standards_results.query["sql"], gluten_result, normal_result, any_exception):
            insert_into_inconsistent_record(standards_results.query["project"], standards_results.query["sql"],
                                            str(gluten_result), str(normal_result))
        else:
            insert_into_response_time(standards_results.query["project"], standards_results.query["sql"],
                                      int(res_time_dict["gluten_res_time"]), int(res_time_dict["normal_res_time"]))
