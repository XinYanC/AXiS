
"""
This file deals with our country-level data.
"""

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

COUNTRY_COLLECTION = 'countries'

ID = 'id'
NAME = 'name'
CODE = 'code'

SAMPLE_COUNTRY = {
    NAME: 'United States',
    CODE: 'US',
}


def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_countries() -> int:
    return len(read())


def create(country):
    if not isinstance(country, dict):
        raise ValueError("Country must be a dictionary.")
    if 'name' not in country or not country['name']:
        raise ValueError("Country must have a non-empty 'name'.")
    if 'code' not in country or not country['code']:
        raise ValueError("Country must have a non-empty 'code'.")

    rec_id = dbc.create(COUNTRY_COLLECTION, country)
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
        return True
    # Otherwise, treat as name and code and delete from database
    ret = dbc.delete(
        COUNTRY_COLLECTION, {NAME: name_or_id, CODE: code}
    )
    if ret < 1:
        raise ValueError(f'Country not found: {name_or_id}, {code}')
    return ret > 0


def read() -> list:
    return dbc.read(COUNTRY_COLLECTION)


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
    # Search in database
    search_lower = search_term.lower().strip()
    matching_countries = {}
    db_countries = dbc.read(COUNTRY_COLLECTION)
    import uuid
    for country_data in db_countries:
        if search_lower in country_data.get(NAME, '').lower():
            # Generate a temporary ID for database countries
            country_id = uuid.uuid4().hex[: max(8, MIN_ID_LEN)]
            matching_countries[country_id] = country_data
    return matching_countries


def main():
    print(read())


if __name__ == '__main__':
    main()
