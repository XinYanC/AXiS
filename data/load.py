#!/usr/bin/env python3
"""
Seed loader — drops and reloads states, cities, and countries
from JSON seed files.

Usage:
    python3 data/load.py
"""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import data.db_connect as dbc  # noqa: E402
import states.queries as stateqry  # noqa: E402
import cities.queries as cityqry  # noqa: E402
import countries.queries as countryqry  # noqa: E402

SEEDS_DIR = os.path.join(os.path.dirname(__file__), 'seeds')


def load_collection(seed_file, create_fn, clear_cache_fn, label):
    seed_path = os.path.join(SEEDS_DIR, seed_file)
    with open(seed_path) as f:
        records = json.load(f)

    # Drop the collection via pymongo directly
    dbc.connect_db()
    collection_name = seed_file.replace('.json', '')
    dbc.client[dbc.GEO_DB][collection_name].drop()

    # Clear the in-memory cache so the next create() starts fresh
    clear_cache_fn()

    loaded = 0
    skipped = 0
    for record in records:
        try:
            create_fn(record, reload=False)
            loaded += 1
        except ValueError as e:
            print(f'  Skipped: {e}')
            skipped += 1

    print(f'{label}: loaded {loaded}, skipped {skipped}')


def main():
    print('Loading seed data into MongoDB...')
    load_collection(
        'states.json', stateqry.create, stateqry.clear_cache, 'states'
    )
    load_collection(
        'cities.json', cityqry.create, cityqry.clear_cache, 'cities'
    )
    load_collection(
        'countries.json', countryqry.create, countryqry.clear_cache,
        'countries'
    )
    print('Done.')


if __name__ == '__main__':
    main()
