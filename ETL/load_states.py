#!/usr/bin/env python3

import sys
import os
import csv

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from states.queries import CODE, NAME, COUNTRY_CODE, create

_DEFAULT_COUNTRY = 'USA'


def extract(flnm: str) -> list:
    state_list = []
    try:
        with open(flnm, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                state_list.append(row)
    except Exception as e:
        print(f'Problem reading file: {e}', file=sys.stderr)
        sys.exit(1)
    return state_list


def transform(state_list: list) -> list:
    if not state_list:
        print('State file is empty.', file=sys.stderr)
        sys.exit(1)

    col_names = [c.strip() for c in state_list.pop(0)]
    col_norm = [c.lower() for c in col_names]
    if 'code' not in col_norm or 'name' not in col_norm:
        print(
            'TSV must include columns: code, name',
            file=sys.stderr,
        )
        sys.exit(1)

    has_country_col = 'country_code' in col_norm

    rev_list = []
    for state in state_list:
        row_dict = {}
        for i, fld in enumerate(col_names):
            key = fld.strip().lower()
            if i >= len(state):
                continue
            row_dict[key] = state[i].strip()

        if has_country_col:
            cc = row_dict.get('country_code', '').strip().upper() or _DEFAULT_COUNTRY
        else:
            cc = _DEFAULT_COUNTRY

        state_dict = {
            CODE: row_dict.get('code', ''),
            NAME: row_dict.get('name', ''),
            COUNTRY_CODE: cc,
        }
        if not state_dict[CODE] or not state_dict[NAME]:
            print('Skipping row with empty code or name', file=sys.stderr)
            continue
        rev_list.append(state_dict)

    return rev_list


def load(rev_list: list) -> None:
    for state in rev_list:
        create(state, reload=False)


def main():
    if len(sys.argv) < 2:
        print('USAGE: load_states.py <tsvfile>')
        print('  Required columns: code, name')
        print('  Optional column: country_code (defaults to USA if omitted).')
        sys.exit(1)

    state_list = extract(sys.argv[1])
    rev_list = transform(state_list)
    load(rev_list)
    print(f'Loaded {len(rev_list)} state(s).')


if __name__ == '__main__':
    main()
