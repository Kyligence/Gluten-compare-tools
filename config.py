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
    'backup': "backup",
    'pt_source_parent_dir': "pt_source_parent_dir",
    'pt_source_file': "pt_source_file",
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

TAGS_LABEL_NOT_FOUND = "NOT_FOUND"
TAGS_LABEL_SQL_ERROR = "SQL_ERROR"
TAGS_LABEL_SUCCESS = "SUCCESS"
TAGS_LABEL_UNRECOGNIZED = "UNRECOGNIZED"
TAGS_LABEL_FALLBACK = "FALLBACK"
TAGS_LABEL_DIFF_20 = "DIFF_DURATION_20"

NOT_SAVE_RECORD_SET: set = {
    TAGS_LABEL_NOT_FOUND, TAGS_LABEL_SQL_ERROR, TAGS_LABEL_DIFF_20
}

NOT_BACKUP_RECORD_SET: set = {
    TAGS_LABEL_NOT_FOUND, TAGS_LABEL_SQL_ERROR
}

tags: (str, str) = {
    "find project": TAGS_LABEL_NOT_FOUND,
    "not found": TAGS_LABEL_NOT_FOUND,
    "Illegal use of": TAGS_LABEL_SQL_ERROR,
    "Was expecting one of": TAGS_LABEL_SQL_ERROR,
    "OBJECT STORAGE Exception": "S3_ERROR"
}

PERFORMANCE_RANGE: list = [-100, -10, -2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2, 10, 100]
