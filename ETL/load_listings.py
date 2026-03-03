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
    MEETUP_LOCATION,
    PRICE,
    NUM_LIKES,
    create,
)


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
    rev_list = []
    col_names = [c.strip() for c in listing_list.pop(0)]

    for row in listing_list:
        listing_dict = {}
        for i, fld in enumerate(col_names):
            if i >= len(row):
                continue
            val = row[i].strip() if i < len(row) else ''
            # Normalize field names to match queries
            key = fld.lower().replace(' ', '_')
            if key == 'title':
                listing_dict[TITLE] = val
            elif key == 'description':
                listing_dict[DESCRIPTION] = val
            elif key == 'transaction_type':
                listing_dict[TRANSACTION_TYPE] = val
            elif key == 'owner':
                listing_dict[OWNER] = val
            elif key in ('meetup_location', 'location'):
                listing_dict[MEETUP_LOCATION] = val
            elif key == 'price':
                if val == '' or val.lower() == 'none':
                    listing_dict[PRICE] = None
                else:
                    try:
                        listing_dict[PRICE] = float(val)
                    except ValueError:
                        listing_dict[PRICE] = None
            elif key == 'num_likes':
                if val == '' or val.lower() == 'none':
                    listing_dict[NUM_LIKES] = 0
                else:
                    try:
                        listing_dict[NUM_LIKES] = int(val)
                    except ValueError:
                        listing_dict[NUM_LIKES] = 0
            elif key == 'images':
                if val == '' or val.lower() == 'none':
                    listing_dict[IMAGES] = []
                else:
                    listing_dict[IMAGES] = [u.strip() for u in val.split(',') if u.strip()]
            else:
                listing_dict[fld] = val
        rev_list.append(listing_dict)

    return rev_list


def load(rev_list: list) -> None:
    for listing in rev_list:
        create(listing, reload=False)


def main():
    if len(sys.argv) < 2:
        print('USAGE: load_listings.py <tsvfile>')
        print('  tsvfile: Tab-separated file with columns such as:')
        print('    title, description, transaction_type, owner, meetup_location,')
        print('    price, num_likes, images')
        sys.exit(1)

    listing_list = extract(sys.argv[1])
    rev_list = transform(listing_list)
    load(rev_list)
    print(f'Loaded {len(rev_list)} listing(s).')


if __name__ == '__main__':
    main()
