import unittest

from collect_goreplay import dispatch


class TestDispatcher(unittest.TestCase):

    def test_dispatch(self):
        dispatch("")


if __name__ == '__main__':
    unittest.main()
