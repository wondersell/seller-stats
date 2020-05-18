import csv

import pytest

from seller_stats.category_stats import CategoryStats


@pytest.fixture()
def sample_category_data(current_path):
    def _sample_category_data(mock='sample_category_transformed', fieldnames=None):
        return list(csv.DictReader(open(current_path + f'/mocks/{mock}.csv'), fieldnames=fieldnames))

    return _sample_category_data


@pytest.fixture()
def sample_category_stats(sample_category_data):
    return CategoryStats(sample_category_data())


@pytest.mark.parametrize('fields, expected_error', [
    [[], 'Required fields not found: id, position, price, purchases, rating, reviews, first_review'],
    [['id'], 'Required fields not found: position, price, purchases, rating, reviews, first_review'],
    [['id', 'position'], 'Required fields not found: price, purchases, rating, reviews, first_review'],
    [['id', 'position', 'price'], 'Required fields not found: purchases, rating, reviews, first_review'],
    [['id', 'position', 'price', 'purchases'], 'Required fields not found: rating, reviews, first_review'],
])
def test_check_dataframe_errors(fields, expected_error, sample_category_data, caplog):
    data = sample_category_data('sample_category_transformed', fieldnames=fields)

    CategoryStats(data)

    for record in caplog.records:
        assert record.levelname == 'WARNING'

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


def test_calculate_basic_stats(sample_category_stats):
    stats = sample_category_stats.calculate_basic_stats()

    assert 'sku' in list(stats.df.columns)
    assert 'turnover' in list(stats.df.columns)
    assert stats.df.loc[0, ].turnover == 357000


def test_calculate_monthly_stats(sample_category_stats):
    stats = sample_category_stats.calculate_monthly_stats()

    assert 'days_since_first_review' in list(stats.df.columns)
    assert 'turnover_month' in list(stats.df.columns)
    assert 'purchases_month' in list(stats.df.columns)

    assert stats.df.loc[0, ].turnover_month == 83671.875
    assert stats.df.loc[0, ].purchases_month == 11.71875
    assert stats.df.loc[0, ].days_since_first_review == 128


def test_top_goods(sample_category_stats):
    top = sample_category_stats.top_goods()

    assert len(top.index) == 5
    assert 'turnover' in list(top.columns)


def test_top_goods_more(sample_category_stats):
    top = sample_category_stats.top_goods(6)

    assert len(top.index) == 6
    assert 'turnover' in list(top.columns)


def test_sales_distribution(sample_category_stats):
    distribution = sample_category_stats.sales_distribution()

    assert len(distribution.index) == 5
    assert 'group' in list(distribution.columns)
    assert 'turnover' in list(distribution.columns)
    assert 'goods' in list(distribution.columns)
    assert 'purchases' in list(distribution.columns)
