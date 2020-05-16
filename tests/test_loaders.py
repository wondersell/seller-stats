import json

import pytest
from scrapinghub import ScrapinghubClient

from seller_stats.loaders import load_scrapinghub, transform_keys


@pytest.fixture
def scrapinghub_api_response():
    def _scrapinghub_api_response(mock):
        with open(f'tests/mocks/{mock}.json') as f:
            json_body = f.read()
            return json.loads(json_body)

    return _scrapinghub_api_response


@pytest.fixture()
def set_scrapinghub_requests_mock(requests_mock, scrapinghub_api_response):
    def _set_scrapinghub_requests_mock(pending_count=1, running_count=1, job_id='123/1/2'):
        requests_mock.get(f'https://storage.scrapinghub.com/items/{job_id}', json=scrapinghub_api_response('scrapinghub_items'))

    return _set_scrapinghub_requests_mock


@pytest.fixture()
def scrapinghub_client():
    return ScrapinghubClient('dummy')


def _test_load_scrapinghub(set_scrapinghub_requests_mock, scrapinghub_client):
    set_scrapinghub_requests_mock(job_id='123/1/1234')

    items = load_scrapinghub(scrapinghub_client, '123/1/1234')

    assert items == []


def test_transform_keys():
    data = [
        {'old_key_one': 1, 'old_key_two': 2, 'old_key_three': 3},
        {'old_key_one': 11, 'old_key_four': 44},
    ]

    data_transformed = transform_keys(data, {'old_key_one': 'one', 'old_key_two': 'two', 'old_key_four': 'four'})

    assert data_transformed[0] == {'one': 1, 'two': 2, 'old_key_three': 3}
    assert data_transformed[1] == {'one': 11, 'four': 44}
