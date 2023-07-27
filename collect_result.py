import argparse
import json
import os
import re
from typing import List

import pandas as pd

import src.compare.compare as compare
from config import NOT_SAVE_RECORD_SET, PERFORMANCE_RANGE, NOT_BACKUP_RECORD_SET, TagsLabel
from config import csv_config, tags, tags_recognized
from src.compare.result import KECompareResultSummary, KECompareItem
from src.database.reader import CsvReader
from src.database.writer import CsvWriter, clean_dirs
from src.entry.response import Response, StandardResult, GoreplayReceive, StandardResultEncoder
from src.rule import SqlRule

# TODO index统计

parser = argparse.ArgumentParser(description='command line arguments')
parser.add_argument('--batch', type=str,
                    help='The execute id.', required=True,
                    default="")

compare_result_writer: CsvWriter
backup: CsvWriter
summary: KECompareResultSummary = KECompareResultSummary()


def statistic_tag_not_response(tag: str):
    if summary.group.get(tag) is None:
        summary.group.setdefault(tag, KECompareItem())

    item = summary.group[tag]
    item.total = item.total + 1
    return


def statistic_tag(tag: str, res: Response):
    statistic_tag_not_response(tag)

    if tag not in NOT_SAVE_RECORD_SET:
        compare_result_writer.insert(tag, res)

    if tag not in NOT_BACKUP_RECORD_SET:
        replay = GoreplayReceive()
        replay.message = res.source_message
        backup.insert(tag, replay)

        if tag == TagsLabel.diff_duration_100:
            dt_total: list = []
            dt_detail: list = []

            for o in res.others:
                dt_total.append(o.response_time)
                dt_detail.append(o.time_trace)

            backup.insert_text(TagsLabel.diff_time,
                               str(dt_total) + str(json.dumps(dt_detail, cls=StandardResultEncoder)))

    return


def issue_2209(res: Response):
    statistic_tag("ISSUE_2209", res)
    return


def unrecognized(res: Response):
    for t in tags_recognized.items():
        if res.source_message.find(t[0]) != -1:
            statistic_tag(t[1], res)
            return

    statistic_tag(TagsLabel.unrecognized, res)

    sm = json.loads(res.source_message)
    item: KECompareItem = summary.group.get(TagsLabel.unrecognized)

    stm: str = re.sub("/\*\+(.)+\*/", "", sm["sql"])

    if stm.startswith("SELECT   * FROM ("):
        stm = stm[17: -20]

    if item.distinct_query.get(stm) is None:
        item.distinct_query[stm] = res.results

    return


def query_failed_others(res: Response):
    statistic_tag("ERROR_UNRECOGNIZED", res)
    return


def fallback_or_index(res: Response) -> bool:
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
        statistic_tag(TagsLabel.fallback, res)

    return fallback


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

    if len(others) > 1:
        query_failed_others(res)

    return


def do_summary(res: Response):
    summary.total = summary.total + 1

    (result, is_replace) = compare.is_consistent(res.results[0], res.results[1], res.exception, res.schema)

    if result and not is_replace:
        fallback: bool = fallback_or_index(res)

        for i in range(0, len(res.others)):
            if fallback:
                while len(summary.fallback_duration) <= i:
                    summary.fallback_duration.append(0)

                summary.fallback_duration[i] = summary.fallback_duration[i] + res.others[i].response_time
            else:
                while len(summary.duration) <= i:
                    summary.duration.append(0)

                summary.duration[i] = summary.duration[i] + res.others[i].response_time

                while len(summary.time_trace) <= i:
                    summary.time_trace.append({})

                for d in res.others[i].time_trace:
                    if d.get("name") not in summary.time_trace[i]:
                        summary.time_trace[i][d.get("name")] = 0

                    summary.time_trace[i][d.get("name")] = summary.time_trace[i][d.get("name")] + d.get("duration")

        statistic_tag(TagsLabel.success, res)

        if len(res.others) == 2:
            summary.duration_diff.append(res.diff_time)
            if res.diff_time < -1:
                statistic_tag(TagsLabel.diff_duration_100, res)
            elif res.diff_time < -0.2:
                statistic_tag(TagsLabel.diff_duration_20, res)

        return

    if result and is_replace:
        issue_2209(res)
        return

    if res.exception:
        do_exception(res.others, res)
        return

    if compare.quick_consistent([res.results[0], res.results[1]], res.exception, res.schema) \
            and res.results[0] is not None and not SqlRule.is_stable_statement(res.source_message):
        statistic_tag(TagsLabel.unstable, res)
        return

    if compare.quick_consistent([res.results[0], res.results[1]], res.exception, res.schema) \
            and res.results[0] is not None and len(res.results[0]) == 500 \
            and SqlRule.is_stable_statement(res.source_message):
        statistic_tag("UNSTABLE500", res)
        return

    unrecognized(res)


def pre_collect(bt: str):
    clean_dirs(csv_config["compare_result"] + os.sep + bt)
    clean_dirs(csv_config["backup"] + os.sep + bt)


def print_time_trace():
    if len(summary.time_trace) < 2:
        return

    keys: set[str] = set()

    for trace in summary.time_trace:
        for key in trace.keys():
            keys.add(key)

    for key in keys:
        t1 = 1
        t2 = 1
        if key in summary.time_trace[0]:
            t1 = summary.time_trace[0][key]

        if key in summary.time_trace[1]:
            t2 = summary.time_trace[1][key]

        compare_result_writer.insert_text("SUMMARY", "{}: {}, {}, AVG: {:.4f}, {:.4f}, DIFF: {:.4f}"
                                          .format(key,
                                                  t1,
                                                  t2,
                                                  t1 / summary.group.get(TagsLabel.success).total,
                                                  t2 / summary.group.get(TagsLabel.success).total,
                                                  t1 / t2))


def collect(bt: str):
    pre_collect(bt)
    global compare_result_writer, backup
    compare_result_writer = CsvWriter(csv_config["compare_result"] + os.sep + bt)
    backup = CsvWriter(csv_config["backup"] + os.sep + bt)

    reader = CsvReader(csv_config["server_result"] + os.sep + bt)

    for file in os.listdir(reader.file_dir):
        if file.endswith(".csv"):
            reader.read_to_other(file, Response(), do_summary)

    compare_result_writer.insert_text("SUMMARY", "Total: {}".format(summary.total))

    if len(summary.duration) < 2:
        compare_result_writer.insert_text("SUMMARY", "Duration: {}".format(summary.duration))
    else:
        compare_result_writer.insert_text("SUMMARY", "Duration: {}, {}, DIFF: {:.4f}"
                                          .format(summary.duration[0],
                                                  summary.duration[1],
                                                  summary.duration[0] / summary.duration[1]))

    print_time_trace()

    for key in summary.group.keys():
        compare_result_writer.insert_text("SUMMARY", "{}: {},".format(key, summary.group.get(key).total))

    if len(summary.duration_diff) != 0:
        cats = pd.cut(summary.duration_diff, PERFORMANCE_RANGE, right=False)
        compare_result_writer.insert_text("SUMMARY", str(pd.value_counts(cats)))

    if summary.group.get(TagsLabel.unrecognized) is not None:
        ung = summary.group.get(TagsLabel.unrecognized)
        compare_result_writer.insert_text("SUMMARY", "")

        compare_result_writer.insert_text("SUMMARY", "{}: distinct count {},".format(TagsLabel.unrecognized,
                                                                                     len(ung.distinct_query.items())))
        for k in ung.distinct_query.keys():
            compare_result_writer.insert_text("SUMMARY", k)
            compare_result_writer.insert_text("SUMMARY", str(ung.distinct_query[k]))
            compare_result_writer.insert_text("SUMMARY", "")


if __name__ == '__main__':
    args = vars(parser.parse_args())
    batch = args["batch"]

    collect(batch)
