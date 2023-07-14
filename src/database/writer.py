import csv
import os

from core.common.config import log
from src.database.datasource import CsvAction, RedisAction
from src.entry.csv_format import CsvFormat


class RedisWriter(RedisAction):
    def __init__(self):
        super().__init__()

    def insert_goreplay(self, batch, record: str):
        if not self.ready():
            return False

        try:
            self.client.lpush(batch, record)
            return True
        except Exception as e:
            log.error("Save record failed", e)
            return False


class CsvWriter(CsvAction):
    file_dir: str = ""

    def __init__(self, sub_dir: str):
        super().__init__(sub_dir)

        self.file_dir = self.parent_dir + os.sep + sub_dir
        if not os.path.exists(self.file_dir):
            log.info("Create dir " + self.file_dir)
            os.makedirs(self.file_dir)

    def insert(self, file_name: str, result: CsvFormat) -> bool:

        if not file_name.endswith(".csv"):
            file_name = file_name + ".csv"

        with open(self.file_dir + os.sep + file_name, "a", newline='') as f:
            writer = csv.writer(f, delimiter=self.delimiter, quotechar=self.quote_char, quoting=self.quoting)
            writer.writerow(result.to_csv_format())

        return True

    def insert_text(self, file_name: str, result: str) -> bool:

        if not file_name.endswith(".csv"):
            file_name = file_name + ".csv"

        with open(self.file_dir + os.sep + file_name, "a", newline='') as f:
            f.write(result + "\n")

        return True


def clean_dirs(dir_path: str):
    csv_writer = CsvWriter(dir_path)

    if not csv_writer.is_ready:
        return

    for file in os.listdir(csv_writer.file_dir):
        if file.endswith(".csv"):
            f_to_delete = csv_writer.file_dir + os.sep + file
            os.remove(f_to_delete)
            log.info("Remove file %s", f_to_delete)
