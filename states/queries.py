
"""
This file deals with our state-level data.
"""
from functools import wraps

import data.db_connect as dbc
from data.db_connect import is_valid_id  # noqa F401

STATE_COLLECTION = 'states'

ID = 'id'
NAME = 'name'
CODE = 'code'
COUNTRY_CODE = 'country_code'

SAMPLE_CODE = 'NY'
SAMPLE_COUNTRY = 'USA'
SAMPLE_KEY = (SAMPLE_CODE, SAMPLE_COUNTRY)
SAMPLE_STATE = {
    NAME: 'New York',
    CODE: SAMPLE_CODE,
    COUNTRY_CODE: SAMPLE_COUNTRY,
}

cache = None


def needs_cache(fn, *args, **kwargs):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not cache:
            load_cache()
        return fn(*args, **kwargs)
    return wrapper


@needs_cache
def count() -> int:
    return len(cache)


@needs_cache
def create(flds: dict, reload=True) -> str:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    code = flds.get(CODE)
    country_code = flds.get(COUNTRY_CODE)
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    if not code:
        raise ValueError(f'Bad value for {code=}')
    if not country_code:
        raise ValueError(f'Bad value for {country_code=}')
    if f'{code},{country_code}' in cache:
        raise ValueError(f'Duplicate key: {code=}; {country_code=}')
    new_id = dbc.create(STATE_COLLECTION, flds)
    print(f'{new_id=}')
    if reload:
        load_cache()
    return new_id


def delete(code: str, cntry_code: str) -> bool:
    ret = dbc.delete(STATE_COLLECTION, {CODE: code, COUNTRY_CODE: cntry_code})
    if ret < 1:
        raise ValueError(f'State not found: {code}, {cntry_code}')
    load_cache()
    return ret


@needs_cache
def read() -> dict:
    return cache


@needs_cache
def search_states_by_name(search_term: str) -> dict:
    """
    Search for states by name (case-insensitive partial match).
    Args:
        search_term: The term to search for in state names
    Returns:
        dict: Dictionary of states matching the search term
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
    matching_states = {}
    for key, state_data in cache.items():
        if search_lower in state_data.get(NAME, '').lower():
            matching_states[key] = state_data
    return matching_states


def load_cache():
    global cache
    cache = {}
    states = dbc.read(STATE_COLLECTION)
    for state in states:
        key = f'{state[CODE]},{state[COUNTRY_CODE]}' # since json can't use tuple as key, use comma-delimited string as key instead
        cache[key] = state


def main():
    create(SAMPLE_STATE)
    print(read())


if __name__ == '__main__':
    main()