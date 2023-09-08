import json
import os
from datetime import date

from flask import Flask, request

from config import csv_config, redis_config
from core.common import config
from src.database.writer import CsvWriter, RedisWriter
from src.entry.response import GoreplayReceive

app = Flask(__name__)


@app.route(config.FORWARD_PATH, methods=['POST'])
def endpoint():
    dispatch(json.dumps(request.get_json()))
    return "Done"


def dispatch(message: str):
    save_to_redis(message)
    save_to_daily_file(message)


def save_to_redis(message: str):
    w = RedisWriter()
    if not w.ready():
        return
    w.insert_goreplay(redis_config["long_running"], message)


def save_to_daily_file(message: str):
    writer = CsvWriter(csv_config["goreplay_data_dir_name"] + os.sep)

    if not writer.ready():
        return

    receive = GoreplayReceive()
    receive.message = message

    writer.insert(str(date.today()), receive)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
