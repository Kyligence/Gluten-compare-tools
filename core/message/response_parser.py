from abc import abstractmethod


class StandardResult(object):
    def __init__(self):
        self.dest = {}
        self.code = ""
        self.response_time = 0
        self.content = ""
        self.exception = ""


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
