import argparse
import os

from config import csv_config
from src.client.kyligence import KE
from src.database.reader import CsvReader
from src.entry.csv_format import CsvFormat
from src.entry.response import GoreplayReceive

parser = argparse.ArgumentParser(description='command line arguments')
parser.add_argument('--batch', type=str,
                    help='', required=True,
                    default="")
parser.add_argument('--tag', type=str,
                    help='', required=True,
                    default="")

if __name__ == '__main__':
    args = vars(parser.parse_args())
    batch = args["batch"]
    tag = args["tag"]


    def read_to_curl(value: CsvFormat):
        ke = KE(value.to_redis_format())
        print(ke.to_readable() + "\n")


    reader = CsvReader(csv_config["backup"] + os.sep + batch)

    for file in os.listdir(reader.file_dir):
        res = reader.read_to_other(tag, GoreplayReceive(), read_to_curl)
