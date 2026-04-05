
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
COUNTRY_CODE = 'country_code'
LATITUDE = 'latitude'
LONGITUDE = 'longitude'

_DEFAULT_COUNTRY = 'USA'

SAMPLE_CITY = {
    NAME: 'Los Angeles',
    STATE_CODE: 'CA',
    COUNTRY_CODE: _DEFAULT_COUNTRY,
    LATITUDE: 34.0522,
    LONGITUDE: -118.2437,
}
SAMPLE_KEY = (
    f'{SAMPLE_CITY[NAME]},{SAMPLE_CITY[STATE_CODE]},'
    f'{SAMPLE_CITY[COUNTRY_CODE]}'
)

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
        cc = (
            str(city.get(COUNTRY_CODE, '') or '')
            .strip()
            .upper()
            or _DEFAULT_COUNTRY
        )
        key = f'{city[NAME]},{city[STATE_CODE]},{cc}'
        doc = dict(city)
        doc[COUNTRY_CODE] = cc
        cache[key] = doc


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


def _require_float_coord(city: dict, fld: str) -> None:
    if fld not in city or city[fld] is None:
        raise ValueError(f"City must have '{fld}'.")
    if isinstance(city[fld], str) and not str(city[fld]).strip():
        raise ValueError(f"City must have a non-empty '{fld}'.")
    try:
        float(city[fld])
    except (TypeError, ValueError):
        raise ValueError(f"'{fld}' must be a number.")


@needs_cache
def create(city, reload=True):
    if not isinstance(city, dict):
        raise ValueError("City must be a dictionary.")
    if NAME not in city or not city[NAME]:
        raise ValueError("City must have a non-empty 'name'.")
    if STATE_CODE not in city or not city[STATE_CODE]:
        raise ValueError("City must have a non-empty 'state_code'.")
    _require_float_coord(city, LATITUDE)
    _require_float_coord(city, LONGITUDE)

    name = city.get(NAME)
    state_code = city.get(STATE_CODE)
    cc = (
        str(city.get(COUNTRY_CODE, '') or '')
        .strip()
        .upper()
        or _DEFAULT_COUNTRY
    )
    cache_key = f'{name},{state_code},{cc}'
    if cache_key in cache:
        raise ValueError(
            f'Duplicate key: {name=}; {state_code=}; {COUNTRY_CODE}={cc!r}'
        )

    doc = dict(city)
    doc[COUNTRY_CODE] = cc
    doc[LATITUDE] = float(doc[LATITUDE])
    doc[LONGITUDE] = float(doc[LONGITUDE])

    rec_id = dbc.create(CITY_COLLECTION, doc)
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
        # name + state_code (+ optional country_code via kwargs in future)
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
