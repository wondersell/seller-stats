def get_distribution_thresholds(series):
    thresholds = list(range(0, max(min([5500, int(series.max())]), 500) + 1, 500))
    labels = []

    for i in range(len(thresholds)):
        if 0 <= i < (len(thresholds) - 1):
            labels.append(f'{thresholds[i]}-{thresholds[i + 1]}')

        if i == (len(thresholds) - 1):
            labels.append(f'>{thresholds[i]}')

    return thresholds, labels
