#!/usr/bin/env python3

import sys
import os
import csv

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from countries.queries import (
    NAME,
    CODE,
    create,
)


def extract(flnm: str) -> list:
    country_list = []
    try:
        with open(flnm) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                country_list.append(row)
    except Exception as e:
        print(f'Problem reading csv file: {str(e)}')
        exit(1)
    return country_list


def transform(country_list: list) -> list:
    rev_list = []
    col_names = country_list.pop(0)

    for country in country_list:
        country_dict = {}
        for i, fld in enumerate(col_names):
            # Map 'country_name' to 'name' and 'country_code' to 'code' for countries.queries
            if fld == 'country_name':
                country_dict[NAME] = country[i]
            elif fld == 'country_code':
                country_dict[CODE] = country[i]
            else:
                country_dict[fld] = country[i]
        rev_list.append(country_dict)

    return rev_list


def load(rev_list: list):
    for country in rev_list:
        create(country, reload=False)


def main():
    if len(sys.argv) < 2:
        print('USAGE: load_countries.py [tsvfile]')
        exit(1)

    country_list = extract(sys.argv[1])
    rev_list = transform(country_list)
    load(rev_list)


if __name__ == '__main__':
    main()
