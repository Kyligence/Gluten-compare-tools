import importlib
import logging
import sys

from core.common import config
from core.result.comparer import Comparer


def get_comparer(model_path, clz_name):
    m = importlib.import_module(model_path)
    clz = getattr(m, clz_name)
    obj = clz()
    if isinstance(obj, Comparer):
        return obj
    else:
        logging.getLogger("Comparer") \
            .error("get_comparer failed: module path({}) and class name({}) is wrong,"
                   "not inherit from Comparer", model_path, clz_name)
        sys.exit(10)


class ResultProcessor(object):
    # ConnectionManager = "ansi"

    def __init__(self):
        self.comparer = get_comparer(config.COMPARER_MODULE_PATH, config.COMPARER_CLASS)

    def compare(self, standards_results):
        self.comparer.compare(standards_results)

