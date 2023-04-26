import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

log = logging.getLogger()

REQUEST_BUILDER_MODULE_PATH = "core.message.ke_request_builder"
REQUEST_BUILDER_CLASS = "KERequestBuilder"

RESPONSE_PARSER_MODULE_PATH = "core.message.ke_response_parser"
RESPONSE_PARSER_CLASS = "KEResponseParser"

COMPARER_MODULE_PATH = "core.result.ke_comparer"
COMPARER_CLASS = "KEComparer"

FORWARD_PATH = "/kylin/api/query"

DEST_URLS = [
    {"tag": "gluten", "url": "http://127.0.0.1:8194/kylin/api/query"},  # ke+gluten,
    {"tag": "normal", "url": "http://127.0.0.1:8195/kylin/api/query"},  # ke+vanilla spark
]

# DROP_TABLE_BEFORE_CREATE = False
