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

tags_recognized: (str, str) = {

}


class _TagsLabel(object):
    @property
    def not_found(self):
        return 'NOT_FOUND'

    @property
    def sql_error(self):
        return 'SQL_ERROR'

    @property
    def success(self):
        return 'SUCCESS'

    @property
    def unrecognized(self):
        return 'UNRECOGNIZED'

    @property
    def fallback(self):
        return 'FALLBACK'

    @property
    def diff_duration_20(self):
        return 'DIFF_DURATION_20'

    @property
    def diff_duration_100(self):
        return 'DIFF_DURATION_100'

    @property
    def diff_time(self):
        return 'DIFF_TIME'

    @property
    def unstable(self):
        return 'UNSTABLE'


TagsLabel = _TagsLabel()

NOT_SAVE_RECORD_SET: set = {
    TagsLabel.not_found, TagsLabel.sql_error, TagsLabel.diff_duration_20, TagsLabel.diff_duration_100,
    TagsLabel.diff_time
}

for t in tags_recognized.items():
    NOT_SAVE_RECORD_SET.add(t[1])

NOT_BACKUP_RECORD_SET: set = {
    TagsLabel.not_found, TagsLabel.sql_error
}

tags: (str, str) = {
    "find project": TagsLabel.not_found,
    "not found": TagsLabel.not_found,
    "Illegal use of": TagsLabel.sql_error,
    "Was expecting one of": TagsLabel.sql_error,
    "OBJECT STORAGE Exception": "S3_ERROR"
}

PERFORMANCE_RANGE: list = [-100, -10, -2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2, 10, 100]
