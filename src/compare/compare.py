def to_string(rows):
    return str([str(x) for x in rows])


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


def quick_consistent(results: list, any_exception: bool, schema: list) -> bool:
    if any_exception:
        return False

    has_none: int = 0
    rows: int = -1

    for result in results:
        if result is None:
            has_none = has_none + 1
        else:
            if rows == -1:
                rows = len(result)

            if rows != len(result):
                return False

            if rows != 0 and len(result[0]) != len(schema):
                return False

    if has_none == 0 or has_none == len(results):
        return True

    return False


def replace_string(s: str) -> str:
    if s is None:
        return "NULL"

    return s.replace("None", "NULL").replace("NaN", "NULL").replace("-Infinity", "NULL").replace("Infinity", "NULL")


def replace_row_result(rows):
    r_new: list = []

    for row in rows:
        if row is None:
            r_new.append("NULL")
            continue

        columns_new = []
        for column in row:
            columns_new.append(replace_string(column))

        r_new.append(columns_new)

    return r_new


def compare(r1: list, r2: list, schema):
    if compare_str(r1, r2):
        return True
    else:
        for row in range(0, len(r1)):
            if compare_str(r2[row], r1[row]):
                continue

            for col in range(0, len(schema)):
                if r2[row][col] == r1[row][col]:
                    continue

                if schema[col].is_float:
                    try:
                        if r2[row][col] is None or r1[row][col] is None:
                            return False

                        gluten_result_float = float(r2[row][col])
                        normal_result_float = float(r1[row][col])
                        if abs(gluten_result_float - normal_result_float) / abs(gluten_result_float) > 0.01:
                            return False
                    except Exception as e:
                        return False
                else:
                    return False

    return True


def is_consistent(gluten_original_result, normal_original_result, any_exception, schema) -> (bool, bool):
    if not quick_consistent([gluten_original_result, normal_original_result], any_exception, schema):
        return False, False

    if compare_str(gluten_original_result, normal_original_result):
        return True, False

    normal_result_sort = sorted(normal_original_result, key=custom_sort)
    gluten_result_sort = sorted(gluten_original_result, key=custom_sort)

    if compare(normal_result_sort, gluten_result_sort, schema):
        return True, False

    r1 = replace_row_result(normal_original_result)
    r2 = replace_row_result(gluten_original_result)
    r1_sort = sorted(r1, key=custom_sort)
    r2_sort = sorted(r2, key=custom_sort)

    return compare(r1_sort, r2_sort, schema), True
