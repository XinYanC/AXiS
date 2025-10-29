
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


def create(city):
    if not isinstance(city, dict):
        raise ValueError("City must be a dictionary.")
    if 'name' not in city or not city['name']:
        raise ValueError("City must have a non-empty 'name'.")
    if 'state_code' not in city or not city['state_code']:
        raise ValueError("City must have a non-empty 'state_code'.")

    import uuid
    rec_id = uuid.uuid4().hex[: max(8, MIN_ID_LEN)]

    city_cache[rec_id] = city
    return rec_id



def delete(city_id: str) -> bool:
    if city_id not in city_cache:
        raise ValueError(f'No such city: {city_id}')
    del city_cache[city_id]
    return True

    
def read() -> dict:
    return city_cache


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
        raise ValueError(f'Search term must be a string, got {type(search_term)}')
    if not search_term.strip():
        raise ValueError('Search term cannot be empty')
    
    cities = read()
    search_lower = search_term.lower().strip()
    matching_cities = {}
    
    for city_id, city_data in cities.items():
        if search_lower in city_data.get(NAME, '').lower():
            matching_cities[city_id] = city_data
    
    return matching_cities


def main():
    print(read())


if __name__ == '__main__':
    main()