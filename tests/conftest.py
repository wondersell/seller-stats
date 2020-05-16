import os

import pytest
import requests_mock


@pytest.fixture()
def current_path():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(autouse=True)
def requests_mocker():
    """Mock all requests.
    This is an autouse fixture so that tests can't accidentally
    perform real requests without being noticed.
    """
    with requests_mock.Mocker() as m:
        yield m
