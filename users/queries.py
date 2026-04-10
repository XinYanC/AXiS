
"""
This file deals with our user-level data.
"""
from datetime import datetime, timezone
from functools import wraps
from bson import ObjectId
import data.db_connect as dbc
from data.db_connect import is_valid_id  # noqa F401
import bcrypt


MIN_ID_LEN = 1

USER_COLLECTION = 'users'

USERNAME = 'username'
PASSWORD = 'password'  # will be hashed
NAME = 'name'
AGE = 'age'
BIO = 'bio'
IS_VERIFIED = 'is_verified'
EMAIL = 'email'  # must end in .edu
CITY = 'city'
STATE = 'state'
COUNTRY = 'country'
RATING = 'rating'
CREATED_AT = 'created_at'
UPDATED_AT = 'updated_at'
SAVED_LISTINGS = 'saved_listings'  # list of listing IDs the user has liked

SAMPLE_USER = {
    USERNAME: 'testuser',
    PASSWORD: 'hashedpassword123',
    NAME: 'Test User',
    AGE: 25,
    BIO: 'This is a test user',
    IS_VERIFIED: False,
    EMAIL: 'testuser@example.edu',
    CITY: 'New York',
    STATE: 'NY',
    COUNTRY: 'USA',
    RATING: 5.0,
    SAVED_LISTINGS: [],
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


def clear_cache():
    """Clear the cache. Useful for testing."""
    global cache
    cache = None


def _normalize_rating(value):
    if value is None or value == '':
        return None
    try:
        rating = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("'rating' must be a number.") from exc
    if rating < 0 or rating > 5:
        raise ValueError("'rating' must be between 0 and 5.")
    return rating


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
    for fld in (CITY, STATE, COUNTRY):
        if fld not in user or not str(user.get(fld) or '').strip():
            raise ValueError(f"User must have a non-empty '{fld}'.")
    if RATING in user:
        user[RATING] = _normalize_rating(user[RATING])
    if PASSWORD in user and user[PASSWORD]:
        password_bytes = user[PASSWORD].encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        user[PASSWORD] = hashed.decode('utf-8')

    if SAVED_LISTINGS in user and user[SAVED_LISTINGS] is not None:
        if not isinstance(user[SAVED_LISTINGS], list):
            raise ValueError("'saved_listings' must be a list.")
    else:
        user[SAVED_LISTINGS] = []

    user[CREATED_AT] = datetime.now(timezone.utc).isoformat()

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


USER_UPDATE_ALLOWED = {
    NAME, AGE, BIO, IS_VERIFIED, CITY, STATE, COUNTRY, RATING,
    SAVED_LISTINGS, PASSWORD
}


@needs_cache
def update(username_or_id: str, update_dict: dict) -> dict:
    """
    Update a user by username or MongoDB ObjectId.
    Allowed fields: name, age, bio, is_verified, city, state, country,
    rating, saved_listings, password (will be hashed).
    Username and email cannot be changed.
    Returns the updated user from cache (without password).
    """
    if not update_dict or not isinstance(update_dict, dict):
        raise ValueError("Update must be a non-empty dictionary.")
    allowed = {
        k: update_dict[k] for k in update_dict if k in USER_UPDATE_ALLOWED
    }
    if not allowed:
        raise ValueError(
            "Update must contain at least one allowed field: "
            "name, age, bio, is_verified, city, state, country, rating, "
            "saved_listings, password."
        )
    if USERNAME in update_dict:
        raise ValueError("Username cannot be updated.")
    if SAVED_LISTINGS in allowed and allowed[SAVED_LISTINGS] is not None:
        if not isinstance(allowed[SAVED_LISTINGS], list):
            raise ValueError("'saved_listings' must be a list.")
    if RATING in allowed:
        allowed[RATING] = _normalize_rating(allowed[RATING])
    for fld in (CITY, STATE, COUNTRY):
        if fld in allowed and (
            allowed[fld] is None or not str(allowed[fld]).strip()
        ):
            raise ValueError(f"'{fld}' must be non-empty.")
    if PASSWORD in allowed and allowed[PASSWORD]:
        password_bytes = str(allowed[PASSWORD]).encode('utf-8')
        allowed[PASSWORD] = bcrypt.hashpw(
            password_bytes, bcrypt.gensalt()
        ).decode('utf-8')
    # by ObjectId
    if len(username_or_id) == 24:
        try:
            obj_id = ObjectId(username_or_id)
            result = dbc.update(
                USER_COLLECTION, {dbc.MONGO_ID: obj_id}, allowed
            )
            if result.matched_count < 1:
                raise ValueError(f'User not found: {username_or_id}')
            load_cache()
            updated = dbc.read_one(USER_COLLECTION, {dbc.MONGO_ID: obj_id})
            if updated:
                updated.pop(PASSWORD, None)
                return updated
            return {}
        except Exception:
            pass
    # By username
    if username_or_id not in cache:
        raise ValueError(f'User not found: {username_or_id}')
    result = dbc.update(
        USER_COLLECTION, {USERNAME: username_or_id}, allowed
    )
    if result.matched_count < 1:
        raise ValueError(f'User not found: {username_or_id}')
    load_cache()
    updated = cache.get(username_or_id)
    if updated:
        out = dict(updated)
        out.pop(PASSWORD, None)
        return out
    return {}


@needs_cache
def read() -> dict:
    return cache


@needs_cache
def find_user_by_email(email: str):
    """
    Return the user dict for the given email, or None if not found.
    Email match is case-insensitive.
    """
    if not email or not isinstance(email, str) or not email.strip():
        return None
    email_lower = email.strip().lower()
    for user in cache.values():
        if (user.get(EMAIL) or '').strip().lower() == email_lower:
            return user
    return None


@needs_cache
def authenticate(email: str, password: str):
    """
    Authenticate a user by email and password.
    Returns the user dict (without password field) if valid, else None.
    """
    if not password or not isinstance(password, str):
        return None
    user = find_user_by_email(email)
    if not user or PASSWORD not in user or not user[PASSWORD]:
        return None
    hashed = user[PASSWORD]
    # bcrypt.checkpw() needs bytes; stored hash may be str from DB
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), hashed):
        return None
    # Return a copy of user without the password field
    out = dict(user)
    out.pop(PASSWORD, None)
    return out


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
