import logging
from datetime import datetime

import numpy as np
import pandas as pd

logger = logging.getLogger('CategoryStats')


class CategoryStats:
    def __init__(self, data):
        self.df = pd.DataFrame()
        self.load_data(data)
        self._check_dataframe()
        self._clean_dataframe()

    def load_data(self, data):
        self.df = pd.DataFrame(data)
        return self

    def _clean_dataframe(self):
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

        self.df['rating'].replace(0, np.nan, inplace=True)

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

        return self

    def calculate_monthly_stats(self):
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

        return self

    def top_goods(self, count):
        df_slice = self.df.loc[:, ['id', 'turnover']]

        return df_slice.groupby(by='id').sum().sort_values(by=['turnover'], ascending=False).head(count)

    def sales_distribution(self, groups=None):
        distribution = []
        groups = groups or (0, 10, 100, 1000)

        for threshold in groups:
            distribution[threshold] = len(self.df[self.df['purchases'] > threshold]) / len(self.df.index)

    def category_name(self):
        return self.df.loc[0, 'category_name'] if 'category_name' in self.df.columns else 'Неизвестная категория'

    def category_url(self):
        return self.df.loc[0, 'category_url'] if 'category_url' in self.df.columns else '–'
