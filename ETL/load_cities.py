#!/usr/bin/env python3

import sys
import os
import csv

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from cities.queries import (
    NAME,
    STATE_CODE,
    create,
)


def extract(flnm: str) -> list:
    cities_list = []
    try:
        with open(flnm) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                cities_list.append(row)
    except Exception as e:
        print(f'Problem reading csv file: {str(e)}')
        exit(1)
    return cities_list


def transform(cities_list: list, state_code: str = None) -> list:
    rev_list = []
    col_names = cities_list.pop(0)

    for city in cities_list:
        cities_dict = {}
        for i, fld in enumerate(col_names):
            # Map 'city_name' to 'name' for cities.queries
            if fld == 'city_name':
                cities_dict[NAME] = city[i]
            else:
                cities_dict[fld] = city[i]

        # Override state_code if provided as argument
        if state_code:
            cities_dict[STATE_CODE] = state_code
        rev_list.append(cities_dict)

    return rev_list


def load(rev_list: list):
    for city in rev_list:
        create(city, reload=False)


def main():
    if len(sys.argv) < 2:
        print('USAGE: load_cities.py [tsvfile] [state_code]')
        print('  tsvfile: Tab-separated file with city data')
        print('  state_code: (optional) Override state_code for all cities')
        exit(1)

    cities_list = extract(sys.argv[1])
    state_code = sys.argv[2] if len(sys.argv) > 2 else None
    rev_list = transform(cities_list, state_code)
    load(rev_list)


if __name__ == '__main__':
    main()
