#!/usr/bin/env python3
"""Small utility to load JSON seed files into MongoDB via the project's
`data.db_connect` helper.

Usage:
  python data/load_seed.py --file data/seeds/cities.json
    --collection cities [--drop]
Like:
    python data/load_seed.py --file data/seeds/countries.json
        --collection countries --drop
    python data/load_seed.py --file data/seeds/states.json
        --collection states --drop
    python data/load_seed.py --file data/seeds/cities.json
        --collection cities --drop
To load to cloud:
    CLOUD_MONGO=1 MONGO_USER='youruser' MONGO_PASSWD='yourpass'
    python data/load_seed.py --file data/seeds/countries.json
        --collection countries --drop

To confirm count after loading:
    python - <<PY
    from data import db_connect
    c = db_connect.connect_db()
    db = c[db_connect.GEO_DB]
    print('countries:', db['countries'].count_documents({}))
    print('cities:', db['cities'].count_documents({}))
    print('states:', db['states'].count_documents({}))
    PY
Or:
    python -c "from data import db_connect; c = db_connect.connect_db(); "
    "print(list(c[db_connect.GEO_DB]['cities'].find().limit(2)))"
"""
import argparse
import json
import sys
from typing import Any

from data import db_connect


def load_file(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--file', required=True,
        help='Path to JSON file (array of objects)'
    )
    p.add_argument(
        '--collection', required=True,
        help='Mongo collection name'
    )
    p.add_argument(
        '--db', default=db_connect.GEO_DB,
        help='Mongo DB name (optional)'
    )
    p.add_argument(
        '--drop', action='store_true',
        help='Drop collection before inserting'
    )
    args = p.parse_args()

    try:
        data = load_file(args.file)
    except Exception as e:
        print(f'Failed to load file {args.file}: {e}', file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, list):
        print(
            'Seed file must contain a JSON array of objects',
            file=sys.stderr
        )
        sys.exit(2)

    client = db_connect.connect_db()
    coll = client[args.db][args.collection]

    if args.drop:
        print(
            f'Dropping collection {args.db}.{args.collection} (per --drop)'
        )
        coll.drop()

    if len(data) == 0:
        print('No documents to insert')
        return

    try:
        res = coll.insert_many(data)
        print(
            f'Inserted {len(res.inserted_ids)} documents into '
            f'{args.db}.{args.collection}'
        )
    except Exception as e:
        print(f'Failed to insert documents: {e}', file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    main()
