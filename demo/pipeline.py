import json
import argparse

import pandas as pd

from candev.core import surprisingness, VariableSummarizer

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, help='Config JSON file.')
parser.add_argument('dataset', type=str, help='CSV file with data to analyze.')

args = parser.parse_args()

# PARSE CONFIG
with open(args.config, 'r') as f:
    config = json.load(f)

# LOAD DATASET
dataset = pd.read_csv(args.dataset)

def get_variable_sorted_by_date(dataset, variable):
    """Get variable sorted by date as list."""
    dataset_restricted_to_variable = dataset.loc[
        dataset[config['variable_column_name']] == variable,
        [config['date_column_name'], config['value_column_name']],
    ].copy()
    dataset_restricted_to_variable['sortable_date'] = pd.to_datetime(dataset_restricted_to_variable[config['date_column_name']])
    sorted_dataset_restricted_to_variable = dataset_restricted_to_variable.sort_values(by='sortable_date')
    return sorted_dataset_restricted_to_variable[config['value_column_name']].tolist()

vars_for_ranking = {
    'variable_name': dataset[config['variable_column_name']].unique(),
    'surprisingness': [],
}
for variable in vars_for_ranking['variable_name']:
    vars_for_ranking['surprisingness'].append(
        surprisingness(
            get_variable_sorted_by_date(dataset, variable),
            config['surprisingness_time_window'],
        )
    )

vars_for_ranking = pd.DataFrame(vars_for_ranking)
sorted_vars_for_ranking = vars_for_ranking.sort_values(by='surprisingness', ascending=False)

document_variables = {
    "main_outcome": get_variable_sorted_by_date(
            dataset, config['main_outcome_name']
        ),
    "long_form_outcomes": {
        sorted_vars_for_ranking['variable_name'][
            i
        ]: get_variable_sorted_by_date(
            dataset, sorted_vars_for_ranking['variable_name'][i]
        )
        for i in range(config['formatting']['num_long_form'])
    },
    "short_form_outcomes": {
        sorted_vars_for_ranking['variable_name'][
            i
        ]: get_variable_sorted_by_date(
            dataset, sorted_vars_for_ranking['variable_name'][i]
        )
        for i in range(
            config['formatting']['num_long_form'],
            config['formatting']['num_long_form'] + config['formatting']['num_short_form'],
        )
    },
}

# GET DOCUMENT COMPONENTS
document_components = {
    'main_outcome': [
        VariableSummarizer(
            config['main_outcome_name'], document_variables['main_outcome']
        ).long_quantitative_summary()
    ],
    'long_form_outcomes': [
        VariableSummarizer(
            key, document_variables['long_form_outcomes'][key]
        ).long_quantitative_summary()
        for key in document_variables['long_form_outcomes']
    ],
    'short_form_outcomes': [
        VariableSummarizer(
            key, document_variables['short_form_outcomes'][key]
        ).short_quantitative_summary()
        for key in document_variables['short_form_outcomes']
    ],
}

document_list = ['# {}'.format(config['dataset_name'])]
document_list.extend(document_components['main_outcome'])
document_list.append('## Major movers')
document_list.extend(document_components['long_form_outcomes'])
document_list.append('## Others')
document_list.extend(document_components['short_form_outcomes'])

document_string = '\n\n'.join(document_list)

with open(config['dataset_name'] + '.md', 'w') as f:
    f.write(document_string)
