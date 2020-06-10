import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataSet:
    fields_required = ()
    fields_force_from_empty_string_to_nan = ()
    fields_force_zeros_to_nan = ()
    fields_drop_empty_strings = ()
    fields_drop_na = ()
    fields_force_types = {}

    def __init__(self, data):
        self.df = pd.DataFrame
        self.meta = {}

        pd.set_option('display.precision', 2)
        pd.set_option('chop_threshold', 0.01)
        pd.options.display.float_format = '{:.2f}'.format

        self.meta['loaded_data'] = {
            'count_raw': len(data),
            'count_removed': 0,
            'count_clean': 0,
            'errors': [],
            'warnings': [],
        }

        self.df = pd.DataFrame(data=data)
        self._check_dataframe()
        self._clean_dataframe()

    def _check_dataframe(self):
        not_found = []

        for field in self.fields_required:
            if field not in self.df.columns.values:
                self.df[field] = None
                not_found.append(field)

        if len(not_found) > 0:
            message = 'Required fields not found: ' + ', '.join(not_found)
            self.meta['loaded_data']['warnings'].append(message)
            logger.warning(message)

    def _clean_dataframe(self):
        len_raw = len(self.df.index)

        # если уж найдем пустые значения, то изгоним их каленым железом (вместе со всей строкой, да)
        for field in self.fields_drop_empty_strings:
            self.df.drop(self.df[self.df[field] == ''].index, inplace=True)

        # делаем пустые значения действительно пустыми
        for field in self.fields_force_from_empty_string_to_nan:
            self.df[field].replace('', np.nan, inplace=True)

        for field in self.fields_force_zeros_to_nan:
            self.df[field].replace(0, np.nan, inplace=True)

        self.df.dropna(subset=self.fields_drop_na, inplace=True)

        for field, field_type in self.fields_force_types.items():
            self.df[field] = self.df[field].astype(field_type)

        len_clean = len(self.df.index)

        self.meta['loaded_data']['count_removed'] = len_raw - len_clean
        self.meta['loaded_data']['count_clean'] = len_clean

        return self
