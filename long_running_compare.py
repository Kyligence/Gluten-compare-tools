import argparse
import os
import time
from datetime import date
from multiprocessing import Pool

from config import csv_config, redis_config
from core.common.config import log
from src.client.kyligence import KE
from src.database.reader import RedisReader
from src.database.writer import CsvWriter

parser = argparse.ArgumentParser(description='command line arguments')
parser.add_argument('--process', type=int,
                    help='Child process number.', required=False,
                    default=10)


def sub_process(process_number: int):
    log.info('Run child process %s (%s)...' % (str(process_number), os.getpid()))
    r = RedisReader()
    if not r.ready():
        log.warn("Redis not ready.")
        log.info('Stop child process %s (%s)...' % (str(process_number), os.getpid()))
        return

    while True:
        source_message = r.read_goreplay(redis_config["long_running"])

        if source_message is None:
            time.sleep(1)
            continue

        if source_message == "":
            time.sleep(1)
            continue

        csv_writer = CsvWriter(csv_config["long_running_result"] + os.sep + str(date.today()))
        log.info('Child process %s (%s) consumer message.' % (str(process_number), os.getpid()))
        ke = KE(source_message)
        csv_writer.insert(str(process_number), ke.query())


if __name__ == '__main__':
    args = vars(parser.parse_args())
    process_num = args["process"]

    log.info("Process num is %d", process_num)

    pool = Pool(process_num)
    for i in range(process_num):
        pool.apply_async(sub_process, args=(i,))

    pool.close()
    pool.join()
