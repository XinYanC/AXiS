
"""
This file deals with our city-level data.
"""

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

CITY_COLLECTION = 'cities'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
}

def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_cities() -> int:
    return len(read())


def create(city):
    if not isinstance(city, dict):
        raise ValueError("City must be a dictionary.")
    if 'name' not in city or not city['name']:
        raise ValueError("City must have a non-empty 'name'.")
    if 'state_code' not in city or not city['state_code']:
        raise ValueError("City must have a non-empty 'state_code'.")

    rec_id = dbc.create(CITY_COLLECTION, city)
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
        return True
    
    # Otherwise, treat as name and state_code and delete from database
    ret = dbc.delete(CITY_COLLECTION, {NAME: name_or_id, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'City not found: {name_or_id}, {state_code}')
    return ret > 0

    
def read() -> list:
    return dbc.read(CITY_COLLECTION)


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
    
    # Search in database
    search_lower = search_term.lower().strip()
    matching_cities = {}
    
    db_cities = dbc.read(CITY_COLLECTION)
    import uuid
    for city_data in db_cities:
        if search_lower in city_data.get(NAME, '').lower():
            # Generate a temporary ID for database cities
            city_id = uuid.uuid4().hex[: max(8, MIN_ID_LEN)]
            matching_cities[city_id] = city_data
    
    return matching_cities


def main():
    print(read())


if __name__ == '__main__':
    main()