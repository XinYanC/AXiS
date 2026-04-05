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
    COUNTRY_CODE,
    LATITUDE,
    LONGITUDE,
    create,
)

_DEFAULT_COUNTRY = 'USA'

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
    col_names = [c.strip() for c in cities_list.pop(0)]
    has_cc = 'country_code' in col_names

    for city in cities_list:
        cities_dict = {}
        for i, fld in enumerate(col_names):
            key = fld.strip()
            if key == 'city_name':
                cities_dict[NAME] = city[i].strip() if i < len(city) else ''
            elif key == 'latitude':
                cities_dict[LATITUDE] = city[i].strip() if i < len(city) else ''
            elif key == 'longitude':
                cities_dict[LONGITUDE] = city[i].strip() if i < len(city) else ''
            elif key == 'state_code':
                cities_dict[STATE_CODE] = city[i].strip() if i < len(city) else ''
            elif key == 'country_code':
                raw = city[i].strip() if i < len(city) else ''
                cities_dict[COUNTRY_CODE] = raw.upper() if raw else _DEFAULT_COUNTRY
            else:
                cities_dict[key] = city[i].strip() if i < len(city) else ''

        if not has_cc:
            cities_dict[COUNTRY_CODE] = _DEFAULT_COUNTRY
        elif COUNTRY_CODE not in cities_dict or not cities_dict[COUNTRY_CODE]:
            cities_dict[COUNTRY_CODE] = _DEFAULT_COUNTRY

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
        print('  tsvfile: city_name, state_code, latitude, longitude,')
        print(f'           optional country_code (defaults to {_DEFAULT_COUNTRY})')
        print('  state_code: (optional) Override state_code for all cities')
        exit(1)

    cities_list = extract(sys.argv[1])
    state_code = sys.argv[2] if len(sys.argv) > 2 else None
    rev_list = transform(cities_list, state_code)
    load(rev_list)


if __name__ == '__main__':
    main()
