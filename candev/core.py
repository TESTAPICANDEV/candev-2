INCREASED = 'increase'
DECREASED = 'decrease'

import numpy as np
import pandas as pd
from scipy import stats


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
        return ', '.join([self._get_qualitative_main(), self._get_detail()]) + '.'

    def short_quantitative_summary(self):
        return self._get_quantitative_main() + '.'

    def long_quantitative_summary(self):
        return ', '.join([self._get_quantitative_main(), self._get_detail()]) + '.'

    # PRIVATE METHODS FOR STRING SUMMARIES
    def _get_qualitative_main(self):
        qualitative_main =  '{name} {direction}d'.format(
            name=self.name,
            direction=self._get_most_recent_change_label()
        )
        return qualitative_main

    def _get_quantitative_main(self):
        quantitative_prefix = '{name} {direction}d by {change_amount:.1f} ({change_percentage:.1f}%) to {current_value:.1f}'.format(
            name=self.name,
            direction=self._get_most_recent_change_label(),
            change_amount=np.abs(self._get_most_recent_change()),
            change_percentage=np.abs(self._get_most_recent_change_as_percentage()),
            current_value=self.current_value,
        )
        return quantitative_prefix

    def _get_detail(self):
        if self._recent_trend() and self._continues_recent_trend():
            detail = 'the {number_consecutive_months} consecutive months of {direction}s'.format(
                number_consecutive_months=self._get_number_of_previous_months_in_trend() + 1,
                direction=self._get_most_recent_change_label()
            )
        elif self._recent_trend() and not self._continues_recent_trend():
            detail = 'following {number_consecutive_months} consecutive months of {direction}s'.format(
                number_consecutive_months=self._get_number_of_previous_months_in_trend() + 1,
                direction=self._get_previous_change_label()
            )
        elif not self._recent_trend():
            if self._get_historical_changes()[-2] > 0.:
                detail = 'following an increase of {:.1f} the previous month.'.format(self._get_historical_changes()[-2])
            elif self._get_historical_changes()[-2] < 0.:
                detail = 'following a decrease of {:.1f} the previous month.'.format(np.abs(self._get_historical_changes()[-2]))
            else:
                detail = 'following no change the previous month.'
        else:
            raise RuntimeError('Unexpectedly reached end of switch.')

        return detail

    def _continues_recent_trend(self):
        if all(self._get_historical_changes()[-3:] > 0.):
            return True
        elif all(self._get_historical_changes()[-3:] < 0.):
            return True
        else:
            return False

    def _recent_trend(self):
        if all(self._get_historical_changes()[-3:-1] > 0.):
            return True
        elif all(self._get_historical_changes()[-3:-1] < 0.):
            return True
        else:
            return False

    def _get_number_of_previous_months_in_trend(self):
        if self._get_historical_changes()[-2] > 0.:
            reversals = np.argwhere(self._get_historical_changes()[:-1] < 0.)
            if len(reversals) > 0:
                return len(self.historical_data) - np.max(reversals) - 4
            else:
                return len(self.historical_data) - 3
        else:
            reversals = np.argwhere(self._get_historical_changes()[:-1] > 0.)
            if len(reversals) > 0:
                return len(self.historical_data) - np.max(reversals) - 4
            else:
                return len(self.historical_data) - 3

    # QUANTITATIVE METHODS
    def _get_most_recent_change_label(self):
        if self._get_most_recent_change() > 0.0:
            return INCREASED
        elif self._get_most_recent_change() < 0.0:
            return DECREASED
        else:
            return 'did not change'

    def _get_previous_change_label(self):
        if self._get_previous_change() > 0.0:
            return INCREASED
        elif self._get_previous_change() < 0.0:
            return DECREASED
        else:
            return 'did not change'

    def _get_most_recent_change_as_percentage(self):
        return 100 * self._get_historical_changes()[-1] / self.historical_data[-2]

    def _get_most_recent_change(self):
        return self._get_historical_changes()[-1]

    def _get_previous_change(self):
        return self._get_historical_changes()[-2]

    def _get_historical_changes(self):
        return np.diff(self.historical_data)

def strip_nan(x):
    if np.ndim(x) > 1:
        raise ValueError('x must be vector-like, got {}d array instead'.format(np.ndim(x)))
    return np.asarray(x)[~np.isnan(x)]

def surprisingness(historical_data, time_window):
    if np.ndim(historical_data) > 1:
        raise ValueError('historical_data must be vector-like, got {}d array instead'.format(np.ndim(historical_data)))
    cleaned_data = strip_nan(historical_data)

    weights = np.exp(-np.arange(0, len(cleaned_data))/float(time_window))
    surprisingnesses = np.abs(stats.zscore(cleaned_data))
    weighted_surprisingness = np.dot(weights, np.flip(surprisingnesses))

    return weighted_surprisingness
