import json
import os
from datetime import date

from flask import Flask, request

from config import csv_config
from core.common import config
from src.database.writer import CsvWriter
from src.entry.response import GoreplayReceive

app = Flask(__name__)


@app.route(config.FORWARD_PATH, methods=['POST'])
def endpoint():
    dispatch(json.dumps(request.get_json()))
    return "Done"


def dispatch(message: str):
    writer = CsvWriter(csv_config["goreplay_data_dir_name"] + os.sep)

    if not writer.ready():
        return

    receive = GoreplayReceive()
    receive.message = message

    writer.insert(str(date.today()), receive)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
