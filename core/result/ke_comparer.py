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

    if query.lower().find("order by") == -1:
        gluten_result = to_sorted_trans_string(gluten_original_result)
        normal_result = to_sorted_string(normal_original_result)
        if gluten_result == normal_result:
            return True
        else:
            # find the first different column value and check out if is precision problem

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
            # write_csv("./inconsistent_record.csv", "problem query:" + standards_results.query["sql"],
            #           "gluten_result:" + gluten_result, "normal_result:" + normal_result)
            insert_into_inconsistent_record(standards_results.query["project"], standards_results.query["sql"],
                                            gluten_result, normal_result)
        else:
            # write_csv("./response_time.csv", "query:" + standards_results.query["sql"],
            #           "gluten_res_time:" + str(res_time_dict["gluten_res_time"]),
            #           "normal_res_time:" + str(res_time_dict["normal_res_time"]))
            insert_into_response_time(standards_results.query["project"], standards_results.query["sql"],
                                      int(res_time_dict["gluten_res_time"]), int(res_time_dict["normal_res_time"]))
