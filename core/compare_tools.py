import sys
from core.common import config
from core.connection.connection_manager import ConnectionManager
from core.message.message_processor import MessageProcessor
from core.result.result_processor import ResultProcessor

log = config.log


class CompareTools(object):
    # ConnectionManager = "ansi"

    def __init__(self):
        try:
            self.connection_manager = ConnectionManager()
            self.messageProcessor = MessageProcessor()
            self.resultProcessor = ResultProcessor()
            # self.destExceptionStrategy = DestExceptionStrategy()
        except Exception as e:
            log.error(e)
            sys.exit(-1)
