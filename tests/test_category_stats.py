import pytest
import csv
from seller_stats.category_stats import CategoryStats


@pytest.fixture()
def sample_category_data(current_path):
    def _sample_category_data(mock='sample_category_transformed', fieldnames=None):
        return [row for row in csv.DictReader(open(current_path + f'/mocks/{mock}.csv'), fieldnames=fieldnames)]

    return _sample_category_data


@pytest.mark.parametrize('fields, expected_error', [
    [[], 'Required fields not found: position, price, purchases, rating, reviews'],
    [['position'], 'Required fields not found: price, purchases, rating, reviews'],
    [['position', 'price'], 'Required fields not found: purchases, rating, reviews'],
    [['position', 'price', 'purchases'], 'Required fields not found: rating, reviews'],
])
def test_check_dataframe_errors(fields, expected_error, sample_category_data):
    data = sample_category_data('sample_category_transformed', fieldnames=fields)

    with pytest.raises(ValueError) as e_info:
        CategoryStats(data)

    assert str(e_info.value) == expected_error


def test_check_dataframe_correct(sample_category_data):
    data = sample_category_data('sample_category_transformed')

    CategoryStats(data)

    assert 1 == 1  # Проверяем, что никакого исключения не выброшено


def _test_category_stats_get_category_name(stats, sample_category_with_names):
    stats.load_from_list(sample_category_with_names)

    assert stats.get_category_name() == 'Ювелирные иконы'


def _test_category_stats_get_category_url(stats, sample_category_with_names):
    stats.load_from_list(sample_category_with_names)

    assert stats.get_category_url() == 'https://www.wildberries.ru/catalog/yuvelirnye-ukrasheniya/ikony'