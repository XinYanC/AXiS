
"""
This file deals with our state-level data.
"""

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

STATE_COLLECTION = 'states'

ID = 'id'
NAME = 'name'
CODE = 'code'

SAMPLE_STATE = {
    NAME: 'New York',
    CODE: 'NY',
}

def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_states() -> int:
    return len(read())


def create(state):
    if not isinstance(state, dict):
        raise ValueError("State must be a dictionary.")
    if 'name' not in state or not state['name']:
        raise ValueError("State must have a non-empty 'name'.")
    if 'code' not in state or not state['code']:
        raise ValueError("State must have a non-empty 'code'.")

    rec_id = dbc.create(STATE_COLLECTION, state)
    return rec_id



def delete(name_or_id: str, code: str = None) -> bool:
    # If only one argument provided, treat it as an ID (MongoDB _id)
    if code is None:
        # Convert string ID to ObjectId for MongoDB
        try:
            obj_id = ObjectId(name_or_id)
        except Exception:
            raise ValueError(f'Invalid state ID format: {name_or_id}')
        ret = dbc.delete(STATE_COLLECTION, {dbc.MONGO_ID: obj_id})
        if ret < 1:
            raise ValueError(f'State not found: {name_or_id}')
        return True
    
    # Otherwise, treat as name and code and delete from database
    ret = dbc.delete(STATE_COLLECTION, {NAME: name_or_id, CODE: code})
    if ret < 1:
        raise ValueError(f'State not found: {name_or_id}, {code}')
    return ret > 0

    
def read() -> list:
    return dbc.read(STATE_COLLECTION)


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
        raise ValueError(f'Search term must be a string, got {type(search_term)}')
    if not search_term.strip():
        raise ValueError('Search term cannot be empty')
    
    # Search in database
    search_lower = search_term.lower().strip()
    matching_states = {}
    
    db_states = dbc.read(STATE_COLLECTION)
    import uuid
    for state_data in db_states:
        if search_lower in state_data.get(NAME, '').lower():
            # Generate a temporary ID for database states
            state_id = uuid.uuid4().hex[: max(8, MIN_ID_LEN)]
            matching_states[state_id] = state_data
    
    return matching_states


def main():
    print(read())


if __name__ == '__main__':
    main()