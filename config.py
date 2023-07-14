import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

log = logging.getLogger()

redis_config = {
    "key_name": "query"
}

csv_config = {
    'file_dir': "",
    'goreplay_data_dir_name': "goreplay",
    'server_result': "server_result",
    'compare_result': "result",
    'backup': "backup"
}

mysql_config = {
    'enable': False,
    'host': "localhost",
    'port': 3306,
    'database': "",
    'user': 'root',
    'password': '',
    'charset': 'utf8'
}

ke_config = {
    "Authorization": "",
    "urls": [
        "",
        ""
    ]  # The 1st is base line, and others is compare line.
}

tags: (str, str) = {
    "find project": "NOT_FOUND",
    "not found": "NOT_FOUND",
    "Illegal use of": "SQL_ERROR",
    "Was expecting one of": "SQL_ERROR",
    "OBJECT STORAGE Exception": "S3_ERROR"
}
