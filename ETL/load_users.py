#!/usr/bin/env python3

import sys
import os
import csv
import bcrypt

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from users.queries import (
    NAME,
    USERNAME,
    PASSWORD,
    create,
)


def extract(flnm: str) -> list:
    user_list = []
    try:
        with open(flnm) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                user_list.append(row)
    except Exception as e:
        print(f'Problem reading csv file: {str(e)}')
        exit(1)
    return user_list


def transform(user_list: list) -> list:
    rev_list = []
    col_names = user_list.pop(0)

    for user in user_list:
        user_dict = {}
        for i, fld in enumerate(col_names):
            # Map common CSV column names to user field names
            if fld == 'name':
                user_dict[NAME] = user[i]
            elif fld == 'username':
                user_dict[USERNAME] = user[i]
            elif fld == 'password':
                # Hash the password using bcrypt before storing
                password_bytes = user[i].encode('utf-8')
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password_bytes, salt)
                user_dict[PASSWORD] = hashed.decode('utf-8')
            else:
                user_dict[fld] = user[i]
        rev_list.append(user_dict)

    return rev_list


def load(rev_list: list):
    for user in rev_list:
        create(user, reload=False)


def main():
    if len(sys.argv) < 2:
        print('USAGE: load_users.py [tsvfile]')
        exit(1)

    user_list = extract(sys.argv[1])
    rev_list = transform(user_list)
    load(rev_list)


if __name__ == '__main__':
    main()
