from typing import List, Dict

from src.entry.response import Response, StandardResult


class KECompareResult(object):
    project: str
    query: str
    batch: str
    date: str
    result: str
    reason: str
    others: StandardResult

    def __init__(self):
        self.project: str = ""
        self.query: str = ""
        self.batch: str = ""
        self.date: str = ""
        self.result: str = ""
        self.reason: str = ""
        self.others: StandardResult = {}


class KECompareItem(object):
    total: int
    details: List[Response]

    def __init__(self):
        self.total: int = 0
        self.details: List[Response] = []


class KECompareResultSummary(object):
    total: int
    duration: List[int]
    group: Dict[str, KECompareItem]

    def __init__(self):
        self.total: int = 0
        self.duration: List[int] = []
        self.group: Dict[str, KECompareItem] = {}
