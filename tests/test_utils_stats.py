import numpy as np
import pandas as pd
import pytest

from seller_stats.utils.stats import get_distribution_thresholds


@pytest.mark.parametrize('mock_data, mock_thresholds, mock_labels', [
    [(1, 450, 1294, 2455, 3964, 4345), [0, 500, 1000, 1500, 2000, 2500, 4346], ['0-500', '500-1000', '1000-1500', '1500-2000', '2000-2500', '>2500']],
    [(345, 678), [0, 100, 200, 300, 400, 500, 679], ['0-100', '100-200', '200-300', '300-400', '400-500', '>500']],
    [(123, 222, 359, 486), [0, 50, 100, 150, 200, 250, 487], ['0-50', '50-100', '100-150', '150-200', '200-250', '>250']],
])
def test_distribution_thresholds_simple(mock_data, mock_thresholds, mock_labels):
    series = pd.Series(data=mock_data)
    thresholds, labels = get_distribution_thresholds(series)

    assert thresholds == mock_thresholds
    assert labels == mock_labels


@pytest.mark.parametrize('batches_count', [1, 5, 10, 100])
def test_distribution_thresholds_count_batches(batches_count):
    # простое линейное случайное распределение
    min_price, max_price = 1, 50000
    data = (max_price - min_price) * np.random.rand(200) + min_price

    series = pd.Series(data=data)

    thresholds, labels = get_distribution_thresholds(series, batches=batches_count)
    assert len(thresholds) == batches_count + 1
    assert len(labels) == batches_count


def test_distribution_thresholds_oneoffs():
    # простое линейное случайное распределение + 1 большой выброс
    min_price, max_price = 1, 50000
    data = (max_price - min_price) * np.random.rand(5) + min_price
    data_max = data.max()
    oneoffs = [data_max * 2, data_max * 2 + 1, data_max * 2 + 2]

    # а теперь добавим выброс
    data = np.append(data, oneoffs)

    series = pd.Series(data=data)

    thresholds, labels = get_distribution_thresholds(series)

    assert np.amax(thresholds) > np.amax(oneoffs)

    # предпоследняя отсечка меньше, чем максимально возможное значение изначального распределения
    assert thresholds[len(thresholds) - 2] <= 50000
