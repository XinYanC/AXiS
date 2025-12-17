#!/usr/bin/env python3

import sys
import csv

from states.queries import (
    COUNTRY_CODE,
    create,
)


def extract(flnm: str) -> list:
    state_list = []
    try:
        with open(flnm) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                state_list.append(row)
    except Exception as e:
        print(f'Problem reading csv file: {str(e)}')
        exit(1)
    return state_list


def transform(state_list: list, country_code: str) -> list:
    rev_list = []
    col_names = state_list.pop(0)

    for state in state_list:
        state_dict = {}
        for i, fld in enumerate(col_names):
            state_dict[fld] = state[i]

        state_dict[COUNTRY_CODE] = country_code
        rev_list.append(state_dict)

    return rev_list


def load(rev_list: list):
    for state in rev_list:
        create(state, reload=False)


def main():
    if len(sys.argv) < 3:
        print('USAGE: load_states.py [tsvfile] [country_code]')
        exit(1)

    state_list = extract(sys.argv[1])
    rev_list = transform(state_list, sys.argv[2])
    load(rev_list)


if __name__ == '__main__':
    main()
