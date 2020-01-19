from .constants import *

import numpy as np


class VariableSummarizer(object):
    def __init__(self, name, historical_data):
        self.name = name

        self.historical_data = historical_data

    @property
    def current_value(self):
        return self.historical_data[-1]

    # STRING SUMMARIES
    def short_qualitative_summary(self):
        return self._get_qualitative_main() + '.'

    def long_qualitative_summary(self):
        return ' '.join([self._get_qualitative_main(), self._get_detail()])

    def short_quantitative_summary(self):
        return self._get_quantitative_main() + '.'

    def long_quantitative_summary(self):
        return ' '.join([self._get_quantitative_main(), self._get_detail()])

    # PRIVATE METHODS FOR STRING SUMMARIES
    def _get_qualitative_main(self):
        qualitative_main =  '{name} {direction}'.format(
            name=self.name,
            direction=self._get_most_recent_change_label()
        )
        return qualitative_main

    def _get_quantitative_main(self):
        quantitative_prefix = '{name} {direction} by {change_amount:.1f} ({change_percentage:.1f}%) to {current_value:.1f}'.format(
            name=self.name,
            direction=self._get_most_recent_change_label(),
            change_amount=np.abs(self._get_most_recent_change()),
            change_percentage=np.abs(self._get_most_recent_change_as_percentage()),
            current_value=self.current_value,
        )
        return quantitative_prefix

    def _get_detail(self):
        raise NotImplementedError

    # QUANTITATIVE METHODS
    def _get_most_recent_change_label(self):
        if self._get_most_recent_change() > 0.0:
            return INCREASED
        elif self._get_most_recent_change() < 0.0:
            return DECREASED
        else:
            return 'did not change'

    def _get_most_recent_change_as_percentage(self):
        return 100 * self._get_historical_changes()[-1] / self.historical_data[-2]

    def _get_most_recent_change(self):
        return self._get_historical_changes()[-1]

    def _get_historical_changes(self):
        return np.diff(self.historical_data)

