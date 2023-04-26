import importlib
import logging
import sys

from core.common import config
from core.message.request_builder import RequestBuilder
from core.message.response_parser import ResponseParser

log = config.log


def get_request_builder(model_path, clz_name):
    m = importlib.import_module(model_path)
    clz = getattr(m, clz_name)
    obj = clz()
    if isinstance(obj, RequestBuilder):
        return obj
    else:
        logging.getLogger("RequestBuilder") \
            .error("get_request_builder failed: module path({}) and class name({}) is wrong,"
                   "not inherit from RequestBuilder", model_path, clz_name)
        sys.exit(10)


def get_response_parser(model_path, clz_name):
    m = importlib.import_module(model_path)
    clz = getattr(m, clz_name)
    obj = clz()
    if isinstance(obj, ResponseParser):
        return obj
    else:
        logging.getLogger("ResponseParser") \
            .error("get_response_parser failed: module path({}) and class name({}) is wrong,"
                   "not inherit from ResponseParser", model_path, clz_name)
        sys.exit(10)


class MessageProcessor(object):

    def __init__(self):
        self.requestBuilder = get_request_builder(config.REQUEST_BUILDER_MODULE_PATH, config.REQUEST_BUILDER_CLASS)
        self.responseParser = get_response_parser(config.RESPONSE_PARSER_MODULE_PATH, config.RESPONSE_PARSER_CLASS)

    def forward(self, urls, source_message):
        source_message_parsed = self.requestBuilder.parse_source(source_message)
        source_message_prepared, addition = self.requestBuilder.build_forward_message(source_message_parsed)
        results = self.requestBuilder.send(urls, source_message_prepared, addition)
        return results

    def parse_results(self, results):
        return self.responseParser.parse_dest_response(results)
