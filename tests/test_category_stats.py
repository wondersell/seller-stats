import csv

import pytest

from seller_stats.category_stats import CategoryStats


@pytest.fixture()
def sample_category_data(current_path):
    def _sample_category_data(mock='sample_category_transformed', fieldnames=None):
        return list(csv.DictReader(open(current_path + f'/mocks/{mock}.csv'), fieldnames=fieldnames))

    return _sample_category_data


@pytest.mark.parametrize('fields, expected_error', [
    [[], 'Required fields not found: position, price, purchases, rating, reviews, first_review'],
    [['position'], 'Required fields not found: price, purchases, rating, reviews, first_review'],
    [['position', 'price'], 'Required fields not found: purchases, rating, reviews, first_review'],
    [['position', 'price', 'purchases'], 'Required fields not found: rating, reviews, first_review'],
])
def test_check_dataframe_errors(fields, expected_error, sample_category_data, caplog):
    data = sample_category_data('sample_category_transformed', fieldnames=fields)

    CategoryStats(data)

    for record in caplog.records:
        assert record.levelname == "WARNING"

    assert expected_error in caplog.text


def test_check_dataframe_correct(sample_category_data, caplog):
    data = sample_category_data('sample_category_transformed')

    CategoryStats(data)

    assert len(caplog.records) == 0


def test_category_stats_get_category_name(sample_category_data):
    data = sample_category_data('sample_category_transformed')

    stats = CategoryStats(data)

    assert stats.category_name() == 'Компрессорные станции для автомобиля'


def test_category_stats_get_category_url(sample_category_data):
    data = sample_category_data('sample_category_transformed')

    stats = CategoryStats(data)

    assert stats.category_url() == 'https://www.wildberries.ru/catalog/aksessuary/avtotovary/kompressornye-stantsii'
