from abc import abstractmethod


class RequestBuilder(object):

    def __init__(self):
        pass

    @abstractmethod  # prepared for the case when source and dest have different input format
    def parse_source(self, source_message):
        pass

    @abstractmethod  # prepared for the case when source and dest have different input format
    def build_forward_message(self, source_message_parsed):
        pass

    @abstractmethod
    def send(self, urls, source_message_prepared, addition):
        pass
