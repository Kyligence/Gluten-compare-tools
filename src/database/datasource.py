import csv

import redis

from config import csv_config
from core.common.config import log

csv.field_size_limit(2 * 1024 * 1024 * 1024)


class CsvAction(object):
    delimiter: str = ','
    quote_char: str = '|'
    quoting: int = csv.QUOTE_MINIMAL
    parent_dir: str = ""
    is_ready: bool = False

    def __init__(self, sub_dir: str):
        parent_dir = csv_config["file_dir"].strip()

        if parent_dir == "":
            self.is_ready = False
            log.warn("Csv file dir is not set")
            return

        self.is_ready = True
        self.parent_dir = parent_dir

    def ready(self) -> bool:
        return self.is_ready


class RedisAction(object):
    pool: redis.ConnectionPool = None
    client: redis.Redis = None
    is_ready: bool = False

    def __init__(self):
        try:
            self.pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
            self.client = redis.Redis(connection_pool=self.pool)
            self.client.ping()
            self.is_ready = True
        except Exception as e:
            log.error("Connect redis error")

    def ready(self) -> bool:
        return self.is_ready

    def close(self):
        self.client.close()
