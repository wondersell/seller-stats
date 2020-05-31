def get_distribution_thresholds(series):
    max_series_value = int(series.max())
    thresholds = list(range(0, max(min([5500, max_series_value]), 500) + 501, 500))
    labels = []

    for i in range(len(thresholds)):
        if 0 <= i < (len(thresholds) - 2):
            labels.append(f'{thresholds[i]}-{thresholds[i + 1]}')

        if i == (len(thresholds) - 2):
            labels.append(f'>{thresholds[i]}')

    return thresholds, labels
