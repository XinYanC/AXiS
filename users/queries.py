
"""
This file deals with our user-level data.
"""
from functools import wraps
from bson import ObjectId
import data.db_connect as dbc
from data.db_connect import is_valid_id  # noqa F401


MIN_ID_LEN = 1

USER_COLLECTION = 'users'

USERNAME = 'username'
PASSWORD = 'password'  # will be hashed
NAME = 'name'
AGE = 'age'
BIO = 'bio'
IS_VERIFIED = 'is_verified'
EMAIL = 'email'  # must end in .edu
LOCATION = 'location'
CREATED_AT = 'created_at'
UPDATED_AT = 'updated_at'

SAMPLE_USER = {
    USERNAME: 'testuser',
    PASSWORD: 'hashedpassword123',
    NAME: 'Test User',
    AGE: 25,
    BIO: 'This is a test user',
    IS_VERIFIED: False,
    EMAIL: 'testuser@example.edu',
    LOCATION: 'NY,USA',
}
SAMPLE_KEY = SAMPLE_USER[USERNAME]

cache = None


def needs_cache(fn, *args, **kwargs):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not cache:
            load_cache()
        return fn(*args, **kwargs)
    return wrapper


def load_cache():
    global cache
    cache = {}
    users = dbc.read(USER_COLLECTION)
    for user in users:
        # Use username as the key
        key = user[USERNAME]
        cache[key] = user


@needs_cache
def num_users() -> int:
    return len(cache)


@needs_cache
def create(user, reload=True):
    if not isinstance(user, dict):
        raise ValueError("User must be a dictionary.")
    if USERNAME not in user or not user[USERNAME]:
        raise ValueError("User must have a non-empty 'username'.")
    username = user.get(USERNAME)
    if username in cache:
        raise ValueError(f'Duplicate key: {username=}')
    # Validate email ends in .edu if provided
    if EMAIL in user and user[EMAIL]:
        if not user[EMAIL].endswith('.edu'):
            raise ValueError("Email must end in .edu")

    rec_id = dbc.create(USER_COLLECTION, user)
    if reload:
        load_cache()
    return rec_id


def delete(username_or_id: str) -> bool:
    # Try to treat as ObjectId first (MongoDB _id)
    # ObjectIds are 24 hex characters
    if len(username_or_id) == 24:
        try:
            obj_id = ObjectId(username_or_id)
            ret = dbc.delete(USER_COLLECTION, {dbc.MONGO_ID: obj_id})
            if ret < 1:
                raise ValueError(f'User not found: {username_or_id}')
            load_cache()
            return ret > 0
        except Exception:
            # If ObjectId conversion fails, fall through to username
            pass
    # Otherwise, treat as username, dbc.delete() will return
    # the number of deleted documents
    ret = dbc.delete(USER_COLLECTION, {USERNAME: username_or_id})
    if ret < 1:
        raise ValueError(f'User not found: {username_or_id}')
    load_cache()
    return ret > 0


@needs_cache
def read() -> dict:
    return cache


@needs_cache
def search_users_by_name(search_term: str) -> dict:
    """
    Search for users by name (case-insensitive partial match).
    Args:
        search_term: The term to search for in user names
    Returns:
        dict: Dictionary of users matching the search term
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
    matching_users = {}
    for key, user_data in cache.items():
        name = user_data.get(NAME, '').lower()
        username = user_data.get(USERNAME, '').lower()
        if (search_lower in name) or (search_lower in username):
            matching_users[key] = user_data
    return matching_users


def main():
    create(SAMPLE_USER)
    print(read())


if __name__ == '__main__':
    main()
