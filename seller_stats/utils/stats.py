def get_distribution_thresholds(series):
    thresholds = list(range(0, min([5501, int(series.max()) + 1]), 500))
    labels = []

    if len(thresholds) == 2:
        labels = [thresholds[0] - thresholds[1]]
    else:
        for i in range(len(thresholds)):
            if i == 0 and len(thresholds) > 0:
                labels.append(f'<{thresholds[i + 1]}')

            if 0 < i < (len(thresholds) - 2):
                labels.append(f'{thresholds[i]}-{thresholds[i + 1]}')

            if i == (len(thresholds) - 2):
                labels.append(f'>{thresholds[i]}')

    return thresholds, labels
