import argparse
import os
import shutil
import sys
import time
from multiprocessing import Pool

from collect_result import collect
from config import csv_config, redis_config
from core.common.config import log
from src.client.kyligence import KE
from src.database.reader import CsvReader
from src.database.reader import RedisReader
from src.database.writer import CsvWriter, clean_dirs
from src.database.writer import RedisWriter
from src.entry.csv_format import CsvFormat
from src.entry.response import GoreplayReceive

parser = argparse.ArgumentParser(description='command line arguments')
parser.add_argument('--process', type=int,
                    help='Child process number.', required=False,
                    default=10)
parser.add_argument('--date', type=str,
                    help='The sql data date.Format yyyy-MM-dd', required=False,
                    default="")
parser.add_argument('--batch', type=str,
                    help='The execute id.', required=True,
                    default="")
parser.add_argument('--mod', type=str,
                    help='', required=True,
                    default="date")


def sub_process(process_number: int, batch_name: str):
    log.info('Run child process %s (%s)...' % (str(process_number), os.getpid()))
    r = RedisReader()
    if not r.ready():
        log.warn("Redis not ready.")
        log.info('Stop child process %s (%s)...' % (str(process_number), os.getpid()))
        return

    clean_dirs(csv_config["server_result"] + os.sep + batch)

    csv_writer = CsvWriter(csv_config["server_result"] + os.sep + batch)

    while True:
        source_message = r.read_goreplay(redis_config["key_name"])

        if source_message is None:
            log.info('Stop child process %s (%s)...' % (str(process_number), os.getpid()))
            return

        if source_message == "":
            time.sleep(1)
            continue

        ke = KE(source_message)
        csv_writer.insert(str(process_number), ke.query())


def prepare_redis_data(batch_name: str, dt: str, m: str) -> bool:
    r = RedisReader()
    # clean batch
    while True:
        source_message = r.read_goreplay(redis_config["key_name"])
        if source_message is None:
            break

        log.info("Clean redis data, batch: %s. Maybe saved by last job.", batch_name)

    r.close()

    w = RedisWriter()

    def read_to_redis(value: CsvFormat):
        w.insert_goreplay(redis_config["key_name"], value.to_redis_format())

    if m == "error":
        reader = CsvReader(csv_config["backup"] + os.sep + dt)

        for file in os.listdir(reader.file_dir):
            if file.endswith(".csv") and file != "NOT_FOUND.csv" and file != "SUCCESS.csv":
                result = GoreplayReceive()
                res = reader.read_to_other(file, result, read_to_redis)

                if not res:
                    return False

        return True
    else:
        reader = CsvReader(csv_config["goreplay_data_dir_name"])
        result = GoreplayReceive()
        return reader.read_to_other(dt, result, read_to_redis)


def clean_history_dirs(dirs: str, cur: int, dt: str, md: str):
    reader = CsvReader(dirs)

    files = []
    for file in os.listdir(reader.file_dir):
        if os.path.isdir(reader.file_dir + os.sep + file):
            files.append(int(file))

    files.sort()

    if len(files) < 10:
        return

    for index in range(0, len(files) - 10 + 1):
        if cur == files[index] or (md == "error" and int(dt) == files[index]):
            continue

        log.info("Clean history dirs %d", files[index])
        shutil.rmtree(reader.file_dir + os.sep + str(files[index]))


def clean_history(bt: str, dt: str, md: str):
    current = int(bt)
    clean_history_dirs(csv_config["server_result"], current, dt, md)
    clean_history_dirs(csv_config["compare_result"], current, dt, md)
    clean_history_dirs(csv_config["backup"], current, dt, md)


if __name__ == '__main__':
    args = vars(parser.parse_args())
    process_num = args["process"]
    date = args["date"]
    batch = args["batch"]
    mod = args["mod"]

    if process_num <= 0:
        process_num = 1

    if process_num >= 20:
        process_num = 20

    clean_history(batch, date, mod)
    if not prepare_redis_data(batch, date, mod):
        log.error("Prepare data failed.")
        sys.exit(-1)

    pool = Pool(process_num)
    for i in range(process_num):
        pool.apply_async(sub_process, args=(i, batch,))

    pool.close()
    pool.join()

    collect(batch)
