#!/usr/bin/env python3

import sys
import os
import csv

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from listings.queries import (
    TITLE,
    DESCRIPTION,
    IMAGES,
    TRANSACTION_TYPE,
    OWNER,
    CITY,
    STATE,
    COUNTRY,
    PRICE,
    NUM_LIKES,
    create,
)


def _normalize_header(h: str) -> str:
    return h.strip().lower().replace(' ', '_')


# TSV columns mapped into listing fields (others ignored, e.g. created_at)
_FIELD_BY_HEADER = {
    'title': TITLE,
    'description': DESCRIPTION,
    'transaction_type': TRANSACTION_TYPE,
    'owner': OWNER,
    'city': CITY,
    'state': STATE,
    'country': COUNTRY,
    'price': PRICE,
    'num_likes': NUM_LIKES,
    'images': IMAGES,
}

_REQUIRED_HEADERS = {'title', 'description', 'transaction_type', 'owner',
                     'city', 'state', 'country'}


def extract(flnm: str) -> list:
    listing_list = []
    try:
        with open(flnm, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                listing_list.append(row)
    except Exception as e:
        print(f'Problem reading file: {e}', file=sys.stderr)
        sys.exit(1)
    return listing_list


def transform(listing_list: list) -> list:
    if not listing_list:
        print('Listing file is empty.', file=sys.stderr)
        sys.exit(1)

    raw_headers = listing_list.pop(0)
    col_names = [_normalize_header(c) for c in raw_headers]

    missing = _REQUIRED_HEADERS - set(col_names)
    if missing:
        print(
            f'Missing required column(s): {", ".join(sorted(missing))}',
            file=sys.stderr,
        )
        sys.exit(1)

    rev_list = []
    for row_idx, row in enumerate(listing_list, start=2):
        listing_dict = {}
        for i, hdr in enumerate(col_names):
            if hdr not in _FIELD_BY_HEADER:
                continue
            val = row[i].strip() if i < len(row) else ''
            key = _FIELD_BY_HEADER[hdr]
            if key == PRICE:
                if val == '' or val.lower() == 'none':
                    listing_dict[PRICE] = None
                else:
                    try:
                        listing_dict[PRICE] = float(val)
                    except ValueError:
                        listing_dict[PRICE] = None
            elif key == NUM_LIKES:
                if val == '' or val.lower() == 'none':
                    listing_dict[NUM_LIKES] = 0
                else:
                    try:
                        listing_dict[NUM_LIKES] = int(val)
                    except ValueError:
                        listing_dict[NUM_LIKES] = 0
            elif key == IMAGES:
                if val == '' or val.lower() == 'none':
                    listing_dict[IMAGES] = []
                else:
                    listing_dict[IMAGES] = [
                        u.strip() for u in val.split(',') if u.strip()
                    ]
            else:
                listing_dict[key] = val

        for req in _REQUIRED_HEADERS:
            fld = _FIELD_BY_HEADER[req]
            v = listing_dict.get(fld)
            if v is None or (isinstance(v, str) and not v.strip()):
                print(
                    f'Row {row_idx}: missing or empty required field '
                    f'"{req}"',
                    file=sys.stderr,
                )
                sys.exit(1)

        rev_list.append(listing_dict)

    return rev_list


def load(rev_list: list) -> None:
    for listing in rev_list:
        create(listing, reload=False)


def main():
    if len(sys.argv) < 2:
        print('USAGE: load_listings.py <tsvfile>')
        print('  Required columns: title, description, transaction_type,')
        print('    owner, city, state, country')
        print('  Optional: price, num_likes, images')
        sys.exit(1)

    listing_list = extract(sys.argv[1])
    rev_list = transform(listing_list)
    load(rev_list)
    print(f'Loaded {len(rev_list)} listing(s).')


if __name__ == '__main__':
    main()
