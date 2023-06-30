import logging

from core.common import config
from core.common.writer import write_csv
from core.connection.mysql_client import insert_into_inconsistent_record, insert_into_response_time, \
    insert_into_exception_record
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


def compare_str(str1, str2):
    if str1 == str2:
        return True

    if str1 is None or str2 is None:
        return False

    return to_string(str1) == to_string(str2)


def custom_sort(value):
    if value is None:
        return 'NULL'

    v = []
    for i in range(0, len(value)):
        if value[i] is None:
            v.append("NULL")
        else:
            v.append(value[i])

    return str(v)


def is_consistent(query, gluten_original_result, normal_original_result, any_exception, schema):
    if any_exception:
        return False

    if gluten_original_result is None and normal_original_result is None:
        return True

    if gluten_original_result is None or normal_original_result is None:
        return False

    if len(gluten_original_result) != len(normal_original_result):
        return False

    if len(gluten_original_result) != 0 and (len(gluten_original_result[0]) != len(normal_original_result[0])
                                             or len(schema) != len(normal_original_result[0])):
        return False

    if compare_str(gluten_original_result, normal_original_result):
        return True

    normal_result_sort = sorted(normal_original_result, key=custom_sort)
    gluten_result_sort = sorted(gluten_original_result, key=custom_sort)

    if compare_str(normal_result_sort, gluten_result_sort):
        return True
    else:
        for row in range(0, len(normal_result_sort)):
            if compare_str(gluten_result_sort[row], normal_result_sort[row]):
                continue

            for col in range(0, len(schema)):
                if gluten_result_sort[row][col] == normal_result_sort[row][col]:
                    continue

                if schema[col].is_float:
                    try:
                        if gluten_result_sort[row][col] is None or normal_result_sort[row][col] is None:
                            return False

                        gluten_result_float = float(gluten_result_sort[row][col])
                        normal_result_float = float(normal_result_sort[row][col])
                        if abs(gluten_result_float - normal_result_float) / abs(gluten_result_float) > 0.01:
                            return False
                    except Exception as e:
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
        normal_exception = False

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
                    normal_exception = True

            res_time_dict[standards_results.results[i].dest["tag"] + "_res_time"] = \
                standards_results.results[i].response_time

        consistent = is_consistent(standards_results.query["sql"], gluten_result, normal_result, any_exception, schema)

        if not self.insert_result:
            return consistent

        if normal_exception:
            insert_into_exception_record(standards_results.query["project"], standards_results.query["sql"],
                                         str(gluten_result), str(normal_result))
        elif not consistent:
            insert_into_inconsistent_record(standards_results.query["project"], standards_results.query["sql"],
                                            str(gluten_result), str(normal_result))
        else:
            if if_fallback is None:
                if_fallback = True

            insert_into_response_time(standards_results.query["project"], standards_results.query["sql"],
                                      int(res_time_dict["gluten_res_time"]), int(res_time_dict["normal_res_time"]),
                                      int(if_fallback))

        return consistent
