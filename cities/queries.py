
"""
This file deals with our city-level data.
"""
from functools import wraps

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

CITY_COLLECTION = 'cities'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

SAMPLE_CITY = {
    NAME: 'Los Angeles',
    STATE_CODE: 'CA',
}
SAMPLE_KEY = f'{SAMPLE_CITY[NAME]},{SAMPLE_CITY[STATE_CODE]}'

cache = None


def needs_cache(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not cache:
            load_cache()
        return fn(*args, **kwargs)
    return wrapper


def load_cache():
    global cache
    cache = {}
    cities = dbc.read(CITY_COLLECTION)
    for city in cities:
        # since json can't use tuple as key, use comma-delimited string
        key = f'{city[NAME]},{city[STATE_CODE]}'
        cache[key] = city


def clear_cache():
    """Clear the cache. Useful for testing."""
    global cache
    cache = None


def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


@needs_cache
def num_cities() -> int:
    return len(cache)


@needs_cache
def create(city, reload=True):
    if not isinstance(city, dict):
        raise ValueError("City must be a dictionary.")
    if NAME not in city or not city[NAME]:
        raise ValueError("City must have a non-empty 'name'.")
    if STATE_CODE not in city or not city[STATE_CODE]:
        raise ValueError("City must have a non-empty 'state_code'.")

    name = city.get(NAME)
    state_code = city.get(STATE_CODE)
    if f'{name},{state_code}' in cache:
        raise ValueError(f'Duplicate key: {name=}; {state_code=}')

    rec_id = dbc.create(CITY_COLLECTION, city)
    if reload:
        load_cache()
    return rec_id


def delete(name_or_id: str, state_code: str = None) -> bool:
    # If only one argument provided, treat it as an ID (MongoDB _id)
    if state_code is None:
        # Convert string ID to ObjectId for MongoDB
        try:
            obj_id = ObjectId(name_or_id)
        except Exception:
            raise ValueError(f'Invalid city ID format: {name_or_id}')
        ret = dbc.delete(CITY_COLLECTION, {dbc.MONGO_ID: obj_id})
        if ret < 1:
            raise ValueError(f'City not found: {name_or_id}')
    else:
        # Otherwise, treat as name and state_code and delete from database
        ret = dbc.delete(
            CITY_COLLECTION, {NAME: name_or_id, STATE_CODE: state_code}
        )
        if ret < 1:
            raise ValueError(f'City not found: {name_or_id}, {state_code}')

    load_cache()
    return ret > 0


@needs_cache
def read() -> dict:
    return cache


@needs_cache
def search_cities_by_name(search_term: str) -> dict:
    """
    Search for cities by name (case-insensitive partial match).
    Args:
        search_term: The term to search for in city names
    Returns:
        dict: Dictionary of cities matching the search term
    Raises:
        ValueError: If search_term is not a string or is empty
    """

    if not isinstance(search_term, str):
        raise ValueError(
            f'Search term must be a string, got {type(search_term)}'
        )
    if not search_term.strip():
        raise ValueError('Search term cannot be empty')

    # Search in cache
    search_lower = search_term.lower().strip()
    matching_cities = {}
    for key, city_data in cache.items():
        if search_lower in city_data.get(NAME, '').lower():
            matching_cities[key] = city_data
    return matching_cities


def main():
    print(read())


if __name__ == '__main__':
    main()
