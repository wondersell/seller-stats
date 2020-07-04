import numpy as np


def get_distribution_thresholds(series, batches=6, variants=None):
    variants = variants or [10, 50, 100, 250, 500, 1000, 5000, 10000, 50000, 100000]
    max_series_value = series.max()
    max_series_value_percentile = series.quantile(.95)

    # отклонение максимального значения выборки от конца шкалы для каждой из шкал (выбросы исключены)
    error = np.array(variants).astype(np.float32) * (batches - 1) - max_series_value_percentile

    # конец шкалы должен быть больше максимального значения, так что все обратные случаи обращаем в минус бесконечность
    error[error > 0] = -np.inf

    # нам нужна размерность с минимальным отклонением
    min_error_index = error.argmax()

    batch_size = variants[min_error_index]

    thresholds = list(range(0, batch_size * batches, batch_size))
    thresholds.append(np.maximum(max_series_value, np.max(thresholds)) + 1)

    labels = []
    for i in range(len(thresholds)):
        if 0 <= i < (len(thresholds) - 2):
            labels.append(f'{thresholds[i]}-{thresholds[i + 1]}')

        if i == (len(thresholds) - 2):
            labels.append(f'>{thresholds[i]}')

    return thresholds, labels
