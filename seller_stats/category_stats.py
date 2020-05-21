import logging
from datetime import datetime

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class CategoryStats:
    def __init__(self, data):
        pd.set_option('display.precision', 2)
        pd.set_option('chop_threshold', 0.01)
        pd.options.display.float_format = '{:.2f}'.format

        self.df = pd.DataFrame(data=data)
        self._check_dataframe()
        self._clean_dataframe()

    def _clean_dataframe(self):
        # делаем пустые значения действительно пустыми
        for field in ('position', 'price', 'purchases', 'rating', 'reviews'):
            self.df[field].replace('', np.nan, inplace=True)

        # если уж найдем пустые значения, то изгоним их каленым железом (вместе со всей строкой, да)
        self.df.drop(self.df[self.df['price'] == ''].index, inplace=True)  # это для случая загрузки из словаря
        self.df.drop(self.df[self.df['purchases'] == ''].index, inplace=True)  # это тоже для словаря

        # а это, если загрузили по API
        self.df.dropna(
            subset=[
                'position',
                'price',
                'purchases',
                'rating',
                'reviews',
            ],
            inplace=True,
        )

        self.df['reviews'].replace(0, np.nan, inplace=True)

        self.df = self.df.astype({
            'position': int,
            'price': float,
            'purchases': int,
            'rating': float,
            'reviews': int,
        })

        return self

    def _check_dataframe(self):
        not_found = []

        required_fields = (
            'id',
            'position',
            'price',
            'purchases',
            'rating',
            'reviews',
            'first_review',
        )

        for field in required_fields:
            if field not in self.df.columns.values:
                self.df[field] = None
                not_found.append(field)

        if len(not_found) > 0:
            logger.warning(f'Required fields not found: ' + ', '.join(not_found))

    def calculate_basic_stats(self):
        self.df['sku'] = 1
        self.df['turnover'] = self.df['price'] * self.df['purchases']

        logger.info('Basic stats calculated')

        return self

    def calculate_monthly_stats(self):
        if 'turnover' not in list(self.df.columns):
            self.calculate_basic_stats()

        # сделаем отдельный датафрейм с отзывами
        df_reviews = self.df.loc[:, ['id', 'first_review', 'turnover', 'purchases']]
        df_reviews = df_reviews[
            df_reviews['first_review'].str.len() != 3]  # почему-то определение NaT как NaN не работает
        df_reviews.loc[:, 'first_review'] = pd.to_datetime(df_reviews.loc[:, 'first_review'], utc=True)
        df_reviews.loc[:, 'days_since_first_review'] = (pd.to_datetime(datetime.now(), utc=True) - df_reviews.loc[:, 'first_review']).dt.days

        # отсеиваем те товары, где первый отзыв был сделан менее 30 дней назад
        df_reviews = df_reviews[df_reviews['days_since_first_review'] > 30]

        # и добавим в него данные по обороту и заказам по месяцам
        df_reviews['turnover_month'] = df_reviews['turnover'] / df_reviews['days_since_first_review'] * 30
        df_reviews['purchases_month'] = df_reviews['purchases'] / df_reviews[
            'days_since_first_review'] * 30

        # соеденим все обратно в основной датафрейм
        self.df = self.df.merge(
            df_reviews.loc[:, ['id', 'days_since_first_review', 'turnover_month', 'purchases_month']],
            on='id', how='left')

        logger.info('Monthly stats calculated')

        return self

    def top_goods(self, count=5):
        if 'turnover' not in list(self.df.columns):
            self.calculate_basic_stats()

        df_slice = self.df.loc[:, ['id', 'turnover']]

        logger.info('Top goods calculated')

        return df_slice.groupby(by='id').sum().sort_values(by=['turnover'], ascending=False).head(count)

    def price_distribution(self):
        thresholds, labels = self.get_distribution_thresholds()

        self.df['bin'] = pd.cut(self.df.price, thresholds, labels=labels, include_lowest=True)

        logger.info('Price distributions calculated')

        return self.df.loc[:, ['bin', 'sku', 'turnover_month', 'purchases_month']].groupby(by='bin').sum().reset_index()

    def get_distribution_thresholds(self):
        if 'turnover_month' not in list(self.df.columns) or 'purchases_month' not in list(self.df.columns):
            self.calculate_monthly_stats()

        thresholds = list(range(0, min([5501, int(self.df.price.max()) + 1]), 500))
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

    def category_name(self):
        return self.df.loc[0, 'category_name'] if 'category_name' in self.df.columns else 'Неизвестная категория'

    def category_url(self):
        return self.df.loc[0, 'category_url'] if 'category_url' in self.df.columns else '–'
