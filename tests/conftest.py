import os

import pytest
import requests_mock
from scrapinghub import ScrapinghubClient


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


@pytest.fixture()
def scrapinghub_client():
    return ScrapinghubClient('dummy_scrapinghub_key')


@pytest.fixture()
def sample_category_data_raw(current_path):
    return open(current_path + '/mocks/scrapinghub_items_wb_raw.jl', 'rb').read()


@pytest.fixture()
def set_scrapinghub_requests_mock(requests_mock, sample_category_data_raw):
    def _set_scrapinghub_requests_mock(pending_count=1, running_count=1, job_id='123/1/2', load_content=None):
        if load_content is None:
            load_content = sample_category_data_raw

        requests_mock.get('https://storage.scrapinghub.com/ids/414324/spider/wb', text='1')
        requests_mock.get('https://storage.scrapinghub.com/jobq/414324/count?state=pending&spider=wb', text=f'{pending_count}')
        requests_mock.get('https://storage.scrapinghub.com/jobq/414324/count?state=running&spider=wb', text=f'{running_count}')
        requests_mock.post('https://app.scrapinghub.com/api/run.json', json={'status': 'ok', 'jobid': f'{job_id}'})
        requests_mock.get(f'https://storage.scrapinghub.com/items/{job_id}?meta=_key', content=load_content, headers={'Content-Type': 'application/x-jsonlines; charset=UTF-8'})

    return _set_scrapinghub_requests_mock
