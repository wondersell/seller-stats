from os import environ

import pytest
from scrapinghub import ScrapinghubClient

from seller_stats.loaders import CsvLoader, ScrapinghubLoader
from seller_stats.transformers import WildsearchCrawlerWildberriesTransformer


@pytest.fixture()
def sample_category_data_raw(current_path):
    return open(current_path + '/mocks/scrapinghub_items_wb_raw.jl', 'rb').read()


@pytest.fixture()
def set_scrapinghub_requests_mock(requests_mock, sample_category_data_raw):
    def _set_scrapinghub_requests_mock(pending_count=1, running_count=1, job_id='123/1/2'):
        requests_mock.get('https://storage.scrapinghub.com/ids/414324/spider/wb', text='1')
        requests_mock.get('https://storage.scrapinghub.com/jobq/414324/count?state=pending&spider=wb', text=f'{pending_count}')
        requests_mock.get('https://storage.scrapinghub.com/jobq/414324/count?state=running&spider=wb', text=f'{running_count}')
        requests_mock.post('https://app.scrapinghub.com/api/run.json', json={'status': 'ok', 'jobid': f'{job_id}'})
        requests_mock.get(f'https://storage.scrapinghub.com/items/{job_id}?meta=_key', content=sample_category_data_raw, headers={'Content-Type': 'application/x-jsonlines; charset=UTF-8'})

    return _set_scrapinghub_requests_mock


@pytest.fixture()
def scrapinghub_client():
    return ScrapinghubClient('dummy_scrapinghub_key')


@pytest.fixture()
def sample_csv_file_path(current_path):
    return current_path + '/mocks/scrapinghub_items_wb_raw.csv'


def test_simple_scrapinghub_loader_init_throws_exception():
    with pytest.raises(Exception) as e_info:
        ScrapinghubLoader(job_id='123/4/5')

    assert 'Pass scrapinghub client or set SH_APIKEY env' in str(e_info)


def test_simple_scrapinghub_loader_init_with_env_var():
    environ['SH_APIKEY'] = 'dummy_scrapinghub_key'
    loader = ScrapinghubLoader(job_id='123/4/5')

    assert type(loader.client) is ScrapinghubClient


def test_custom_scrapinghub_loader_init(scrapinghub_client):
    loader = ScrapinghubLoader(job_id='123/4/5', client=scrapinghub_client)

    assert type(loader.client) is ScrapinghubClient


def test_simple_scrapinghub_loader_load(set_scrapinghub_requests_mock, scrapinghub_client):
    set_scrapinghub_requests_mock(job_id='414324/1/735')
    loader = ScrapinghubLoader(job_id='414324/1/735', client=scrapinghub_client)

    data = loader.load()

    assert len(data) == 440
    assert 'product_name' in data[0].keys()
    assert 'wb_id' in data[0].keys()


def test_scrapinghub_loader_with_transformer(set_scrapinghub_requests_mock, scrapinghub_client):
    set_scrapinghub_requests_mock(job_id='414324/1/735')

    transformer = WildsearchCrawlerWildberriesTransformer()
    loader = ScrapinghubLoader(job_id='414324/1/735', client=scrapinghub_client, transformer=transformer)

    data = loader.load()

    assert type(loader.transformer) is WildsearchCrawlerWildberriesTransformer

    assert len(data) == 440
    assert 'product_name' not in data[0].keys()
    assert 'wb_id' not in data[0].keys()
    assert 'name' in data[0].keys()
    assert 'id' in data[0].keys()


def test_simple_csv_loader_init(sample_csv_file_path):
    loader = CsvLoader(file_path=sample_csv_file_path)

    assert loader.file_path == sample_csv_file_path


def test_simple_csv_loader_load(sample_csv_file_path):
    loader = CsvLoader(file_path=sample_csv_file_path)

    data = loader.load()

    assert len(data) == 440
    assert 'product_name' in data[0].keys()
    assert 'wb_id' in data[0].keys()


def test_csv_loader_with_transformer(sample_csv_file_path):
    transformer = WildsearchCrawlerWildberriesTransformer()

    loader = CsvLoader(file_path=sample_csv_file_path, transformer=transformer)

    data = loader.load()

    assert len(data) == 440
    assert 'product_name' not in data[0].keys()
    assert 'wb_id' not in data[0].keys()
    assert 'name' in data[0].keys()
    assert 'id' in data[0].keys()
