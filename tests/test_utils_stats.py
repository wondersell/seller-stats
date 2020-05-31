import pandas as pd
import pytest

from seller_stats.utils.stats import get_distribution_thresholds


@pytest.mark.parametrize('mock_data, mock_thresholds, mock_labels', [
    [(1, 450, 1294, 2455, 3964, 4345), [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500], ['0-500', '500-1000', '1000-1500', '1500-2000', '2000-2500', '2500-3000', '3000-3500', '3500-4000', '>4000']],
    [(345, 678), [0, 500, 1000], ['0-500', '>500']],
    [(123, 222, 359, 486), [0, 500, 1000], ['0-500', '>500']],
])
def test_distribution_thresholds(mock_data, mock_thresholds, mock_labels):
    series = pd.Series(data=mock_data)
    thresholds, labels = get_distribution_thresholds(series)

    assert thresholds == mock_thresholds
    assert labels == mock_labels
