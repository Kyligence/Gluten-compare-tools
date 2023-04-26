from abc import abstractmethod


class Comparer(object):
    # ConnectionManager = "ansi"

    def __init__(self):
        pass

    @abstractmethod
    def compare(self, standards_results):
        pass
