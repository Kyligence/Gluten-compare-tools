import copy
import csv
import os

from core.common.config import log
from src.database.datasource import RedisAction, CsvAction
from src.entry.csv_format import CsvFormat


class RedisReader(RedisAction):

    def __init__(self):
        super().__init__()

    def read_goreplay(self, batch: str) -> str:
        return self.client.rpop(batch)


class CsvReader(CsvAction):
    file_dir: str = ""

    def __init__(self, sub_dir: str):
        super().__init__(sub_dir)

        self.file_dir = self.parent_dir + os.sep + sub_dir

        if not os.path.exists(self.file_dir):
            log.info("Create dir " + self.file_dir)
            os.makedirs(self.file_dir)

    def read_to_other(self, file_name: str, result: CsvFormat, func) -> bool:
        if not file_name.endswith(".csv"):
            file_name = file_name + ".csv"

        if not os.path.exists(self.file_dir + os.sep + file_name):
            log.info("File not found" + file_name)
            return False

        with open(self.file_dir + os.sep + file_name, "r", newline='') as f:
            reader = csv.reader(f, delimiter=self.delimiter, quotechar=self.quote_char, quoting=self.quoting)

            for row in reader:
                r = copy.copy(result)
                r.from_csv_format(row)
                func(r)

        return True
