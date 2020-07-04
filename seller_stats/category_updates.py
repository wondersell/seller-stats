# На данный момент фича заморожена
import os
import tempfile
from urllib.parse import quote, urlencode, urlunparse

import boto3
import pandas as pd
from envparse import env

# инициализируем S3
s3 = boto3.client('s3')


class CategoryListUpdates:
    _columns = ['category_name', 'category_url']
    _types = ['added', 'removed', 'full']

    def fill_types_with(self, value):
        skeleton = {}

        for _t in self._types:
            skeleton[_t] = value

        return skeleton

    def generate_search_url(self, category_name):
        return urlunparse((
            'https',
            'www.wildberries.ru',
            'catalog/0/search.aspx',
            '',
            urlencode({'search': category_name}, quote_via=quote),
            '',
        ))

    def generate_category_type(self, category_url):
        if '/catalog/novinki/' in category_url:
            return 'Новинки'

        if '/promotions/' in category_url:
            return 'Промо'

        return 'Обычная'

    def __init__(self, old, new):
        self.categories_old = old
        self.categories_new = new

        self.diff = self.fill_types_with(pd.DataFrame())
        self.diff_unique = self.fill_types_with(pd.DataFrame())
        self.s3_files = self.fill_types_with(None)

    def load_from_api(self, client, project):
        """Export last two scraped WB categories for comparison."""
        jobs_summary = project.jobs.iter(has_tag=['daily_categories'], state='finished', count=2)

        counter = 0
        job_results = [[], []]

        for job in jobs_summary:
            job_results[counter] = []

            for item in client.get_job(job['key']).items.iter():
                job_results[counter].append({
                    'category_name': item['wb_category_name'],
                    'category_url': item['wb_category_url'],
                })

            counter += 1

        self.categories_old = job_results[0]
        self.categories_new = job_results[1]
        return self

    def add_category_search_url(self):
        for _type in self._types:
            self.diff[_type]['category_search_url'] = self.diff[_type]['category_name'].apply(
                lambda x: self.generate_search_url(x),
            )

    def add_category_type(self):
        for _type in self._types:
            self.diff[_type]['category_type'] = self.diff[_type]['category_url'].apply(
                lambda x: self.generate_category_type(x),
            )

    def sort_by(self, _field):
        for _type in self._types:
            self.diff[_type].sort_values(by=[_field])

    def calculate_diff(self):
        self.calculate_added_diff()
        self.calculate_removed_diff()
        self.calculate_full_diff()

        self.add_category_search_url()
        self.add_category_type()
        self.sort_by('category_type')

    def calculate_full_diff(self):
        """
        Retrieve all different values from two dictionaries.

        Details: https://pythondata.com/quick-tip-comparing-two-pandas-dataframes-and-getting-the-differences/
        """
        df1 = pd.DataFrame(self.categories_old, columns=self._columns)
        df2 = pd.DataFrame(self.categories_new, columns=self._columns)

        df = pd.concat([df1, df2])  # concat dataframes
        df = df.reset_index(drop=True)  # reset the index
        df_gpby = df.groupby(list(df.columns))  # group by

        diff_indexes = [x[0] for x in df_gpby.groups.values() if len(x) == 1]  # reindex

        ri = df.reindex(diff_indexes)

        self.diff['full'] = ri.groupby('category_url', as_index=False).first()
        self.diff_unique['full'] = self.diff['full'].groupby('category_name', as_index=False).first()

        return self

    def calculate_added_diff(self):
        """
        Retrieve only new values from two dictionaries.

        :return:
        """
        df_old = pd.DataFrame(self.categories_old, columns=self._columns)
        df_new = pd.DataFrame(self.categories_new, columns=self._columns)

        df_diff = pd.merge(df_new, df_old, how='outer', indicator=True)
        self.diff['added'] = df_diff.loc[df_diff._merge == 'left_only', self._columns]
        self.diff_unique['added'] = self.diff['added'].groupby('category_name', as_index=False).first()

        return self

    def calculate_removed_diff(self):
        """
        Retrieve only old values from two dictionaries.

        :return:
        """
        df_old = pd.DataFrame(self.categories_old, columns=self._columns)
        df_new = pd.DataFrame(self.categories_new, columns=self._columns)

        df_diff = pd.merge(df_old, df_new, how='outer', indicator=True)
        self.diff['removed'] = df_diff.loc[df_diff._merge == 'left_only', self._columns]
        self.diff_unique['removed'] = self.diff['removed'].groupby('category_name', as_index=False).first()

        return self

    def get_categories_count(self, _type=None) -> int:
        if _type is None:
            raise Exception('type is not defined')

        return len(self.diff[_type])

    def get_categories_unique_count(self, _type=None) -> int:
        if _type is None:
            raise Exception('type is not defined')

        return len(self.diff_unique[_type])

    def dump_to_s3_file(self, _type=None):
        if _type is None:
            raise Exception('type is not defined')

        prefix = _type + '_'
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', prefix=prefix, mode='r+b', delete=True)
        temp_file_name = os.path.basename(temp_file.name)

        self.diff[_type].to_excel(temp_file.name, index=None, header=True)

        s3.upload_file(temp_file.name, env('AWS_S3_BUCKET_NAME'), temp_file_name)

        self.s3_files[_type] = temp_file_name

        return self

    def get_s3_file_name(self, _type=None):
        if _type is None:
            raise Exception('type is not defined')

        return self.s3_files[_type]
