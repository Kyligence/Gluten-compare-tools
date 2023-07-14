import argparse
import os
from typing import List

import src.compare.compare as compare
from config import csv_config, tags
from src.compare.result import KECompareResultSummary, KECompareItem
from src.database.reader import CsvReader
from src.database.writer import CsvWriter, clean_dirs
from src.entry.response import Response, StandardResult, GoreplayReceive

# def collect_summary():
#
#
#
#
#     with open(file_dir + os.sep + file_name, "a", newline='') as f:
#         writer = csv.writer(f, delimiter=super().delimiter, quotechar=super().quote_char, quoting=super().quoting)
#         writer.writerow(result.to_csv_format())

# TODO fallback统计
# TODO index统计

parser = argparse.ArgumentParser(description='command line arguments')
parser.add_argument('--batch', type=str,
                    help='The execute id.', required=True,
                    default="")

summary: KECompareResultSummary = KECompareResultSummary()


def statistic_tag_not_response(tag: str):
    if summary.group.get(tag) is None:
        summary.group.setdefault(tag, KECompareItem())

    item = summary.group[tag]
    item.total = item.total + 1
    return


def statistic_tag(tag: str, res: Response):
    statistic_tag_not_response(tag)

    item = summary.group[tag]
    item.details.append(res)
    return


def issue_2209(res: Response):
    statistic_tag("ISSUE_2209", res)
    return


def unrecognized(res: Response):
    statistic_tag("UNRECOGNIZED", res)
    return


def query_failed_others(res: Response):
    statistic_tag("ERROR_UNRECOGNIZED", res)
    return


def fallback_or_index(res: Response):
    others = res.others

    start_index = 1
    if len(others) <= 1:
        start_index = 0

    fallback: bool = False
    for i in range(start_index, len(others)):
        if others[i].fallback:
            fallback = True
            break

    if fallback:
        statistic_tag("FALLBACK", res)

    return


def do_exception(others: List[StandardResult], res: Response):
    except_cnt: int = 0
    for i in range(0, len(others)):
        if others[i].exception != "":
            except_cnt = except_cnt + 1

    if except_cnt == len(others):
        tag: dict = {}

        for other in others:
            if tag == {}:
                for t in tags.items():
                    if other.exception.find(t[0]) != -1:
                        tag = t
                        break

                if tag == {}:
                    query_failed_others(res)
                    return

            else:
                if other.exception.find(tag[0]) == -1:
                    query_failed_others(res)
                else:
                    statistic_tag(tag[1], res)

                return
    else:
        for other in others:
            for t in tags.items():
                if other.exception.find(t[0]) != -1:
                    statistic_tag(t[1], res)
                    return


def do_summary(res: Response):
    summary.total = summary.total + 1

    (result, is_replace) = compare.is_consistent(res.results[0], res.results[1], res.exception, res.schema)

    if result and not is_replace:
        for i in range(0, len(res.others)):
            while len(summary.duration) <= i:
                summary.duration.append(0)

            summary.duration[i] = summary.duration[i] + res.others[i].response_time

        statistic_tag("SUCCESS", res)
        fallback_or_index(res)
        return

    if result and is_replace:
        issue_2209(res)
        return

    if res.exception:
        do_exception(res.others, res)
        return

    if compare.quick_consistent([res.results[0], res.results[1]], res.exception,
                                res.schema) and res.source_message.find(" limit ") != -1:
        statistic_tag("LIMIT", res)
        return

    unrecognized(res)


def pre_collect(bt: str):
    clean_dirs(csv_config["compare_result"] + os.sep + bt)
    clean_dirs(csv_config["backup"] + os.sep + bt)


def collect(bt: str):
    pre_collect(bt)
    reader = CsvReader(csv_config["server_result"] + os.sep + bt)

    for file in os.listdir(reader.file_dir):
        if file.endswith(".csv"):
            reader.read_to_other(file, Response(), do_summary)

    writer = CsvWriter(csv_config["compare_result"] + os.sep + bt)
    backup = CsvWriter(csv_config["backup"] + os.sep + bt)

    for key in summary.group.keys():
        for res in summary.group[key].details:
            writer.insert(key, res)
            replay = GoreplayReceive()
            replay.message = res.source_message
            backup.insert(key, replay)

    writer.insert_text("SUMMARY", "Total: {}".format(summary.total))
    writer.insert_text("SUMMARY", "Duration: {}".format(summary.duration))

    for key in summary.group.keys():
        writer.insert_text("SUMMARY", "{}: {}".format(key, summary.group.get(key).total))


if __name__ == '__main__':
    args = vars(parser.parse_args())
    batch = args["batch"]

    collect(batch)
