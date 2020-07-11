class BadDataSet(Exception):
    """Raised if data set is empty or incorrect."""


class NotReady(Exception):
    """Raised if we can't extrack data yet, i.e. Scrapinghub job is not finished."""
