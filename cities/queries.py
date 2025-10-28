
"""
This file deals with our city-level data.
"""

import data.db_connect as dbc

MIN_ID_LEN = 1

CITY_COLLECTION = 'cities'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
}

city_cache = {}

def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_cities() -> int:
    return len(city_cache)


def create(flds: dict) -> str:
    dbc.connect_db()
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = dbc.create(CITY_COLLECTION, flds)
    print(f'{new_id}')
    return new_id

def delete(city_id: str) -> bool:
    if city_id not in city_cache:
        raise ValueError(f'No such city: {city_id}')
    del city_cache[city_id]
    return True

    
def read() -> dict:
    return city_cache


def main():
    print(read())


if __name__ == '__main__':
    main()