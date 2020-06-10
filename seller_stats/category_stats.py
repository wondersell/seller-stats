import logging
from datetime import datetime

import pandas as pd

from .base import DataSet
from .utils.stats import get_distribution_thresholds

logger = logging.getLogger(__name__)


class CategoryStats(DataSet):
    fields_required = (
        'id',
        'position',
        'price',
        'purchases',
        'rating',
        'reviews',
        'first_review',
    )

    fields_force_from_empty_string_to_nan = ('position', 'price', 'purchases', 'rating', 'reviews')
    fields_force_zeros_to_nan = ['reviews']
    fields_force_types = {
        'position': 'float',
        'price': 'float',
        'purchases': 'float',
        'rating': 'float',
        'reviews': 'float',
    }

    def __init__(self, data):
        super().__init__(data=data)

        self.calculate_basic_stats()
        self.calculate_monthly_stats()

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

    def category_name(self) -> str:
        return self.df.loc[0, 'category_name'] if 'category_name' in self.df.columns else 'Неизвестная категория'

    def category_url(self) -> str:
        return self.df.loc[0, 'category_url'] if 'category_url' in self.df.columns else '–'


class CategorySliceStats(DataSet):
    pass


class SalesDistributions(DataSet):
    fields_required = ('bin', 'sku', 'turnover_month', 'purchases_month')


def calc_sales_distribution(stats: CategoryStats) -> SalesDistributions:
    thresholds, labels = get_distribution_thresholds(stats.df.price)

    stats.df['bin'] = pd.cut(stats.df.price, thresholds, labels=labels, include_lowest=True)
    data = stats.df.loc[:, ['bin', 'sku', 'turnover_month', 'purchases_month']].groupby(by='bin').sum().reset_index()

    logger.info('Price distributions calculated')

    return SalesDistributions(data=data)


def calc_hhi(stats: CategoryStats, by='brand'):
    total_market = stats.df.turnover_month.sum()

    df_groups = stats.df.loc[:, [by, 'turnover_month']].groupby(by=by).sum()
    df_groups['share'] = df_groups.turnover_month / total_market * 100
    df_groups['sq_share'] = df_groups.share * df_groups.share

    return df_groups.sq_share.sum()
