class BadDataSet(Exception):
    """Raised if data set is empty or incorrect."""


class NotReady(Exception):
    """Raised if we can't extract data yet, i.e. Scrapinghub job is not finished."""
