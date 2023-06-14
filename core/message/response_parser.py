from abc import abstractmethod


class StandardResult(object):
    def __init__(self):
        self.dest = {}
        self.code = ""
        self.response_time = 0
        self.content = None
        self.exception = ""
        self.if_fallback = False
        self.schema = []


class Schema(object):
    name = ""
    is_float = False

    def __init__(self, name, is_float_):
        self.is_float = is_float_
        self.name = name


class StandardResults(object):
    def __init__(self):
        self.query = ""
        self.addition = ""
        self.results = []


class ResponseParser(object):
    def __init__(self):
        pass

    @abstractmethod
    def parse_dest_response(self, results):
        pass
