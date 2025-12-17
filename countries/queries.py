
"""
This file deals with our country-level data.
"""
from functools import wraps

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

COUNTRY_COLLECTION = 'countries'

ID = 'id'
NAME = 'name'
CODE = 'code'

SAMPLE_COUNTRY = {
    NAME: 'France',
    CODE: 'FR',
}
SAMPLE_KEY = SAMPLE_COUNTRY[CODE]

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
    countries = dbc.read(COUNTRY_COLLECTION)
    for country in countries:
        key = country[CODE]  # use country code as key
        cache[key] = country


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
def num_countries() -> int:
    return len(cache)


@needs_cache
def create(country, reload=True):
    if not isinstance(country, dict):
        raise ValueError("Country must be a dictionary.")
    if ('name' not in country or not country['name'] or
            not country['name'].strip()):
        raise ValueError("Country must have a non-empty 'name'.")
    if ('code' not in country or not country['code'] or
            not country['code'].strip()):
        raise ValueError("Country must have a non-empty 'code'.")

    code = country.get(CODE)
    if code in cache:
        raise ValueError(f'Duplicate key: {code=}')

    rec_id = dbc.create(COUNTRY_COLLECTION, country)
    if reload:
        load_cache()
    return rec_id


def delete(name_or_id: str, code: str = None) -> bool:
    # If only one argument provided, treat it as an ID (MongoDB _id)
    if code is None:
        # Convert string ID to ObjectId for MongoDB
        try:
            obj_id = ObjectId(name_or_id)
        except Exception:
            raise ValueError(f'Invalid country ID format: {name_or_id}')
        ret = dbc.delete(COUNTRY_COLLECTION, {dbc.MONGO_ID: obj_id})
        if ret < 1:
            raise ValueError(f'Country not found: {name_or_id}')
    else:
        # Otherwise, treat as name and code and delete from database
        ret = dbc.delete(
            COUNTRY_COLLECTION, {NAME: name_or_id, CODE: code}
        )
        if ret < 1:
            raise ValueError(f'Country not found: {name_or_id}, {code}')

    load_cache()
    return ret > 0


@needs_cache
def read() -> dict:
    return cache


@needs_cache
def search_countries_by_name(search_term: str) -> dict:
    """
    Search for countries by name (case-insensitive partial match).
    Args:
        search_term: The term to search for in country names
    Returns:
        dict: Dictionary of countries matching the search term
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
    matching_countries = {}
    for key, country_data in cache.items():
        if search_lower in country_data.get(NAME, '').lower():
            matching_countries[key] = country_data
    return matching_countries


def main():
    print(read())


if __name__ == '__main__':
    main()
