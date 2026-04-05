"""
This file deals with our listing-level data (marketplace items).
"""
from datetime import datetime, timezone
from functools import wraps

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

LISTING_COLLECTION = 'listings'

ID = 'id'
TITLE = 'title'
DESCRIPTION = 'description'
IMAGES = 'images'
TRANSACTION_TYPE = 'transaction_type'
OWNER = 'owner'
CITY = 'city'
STATE = 'state'
COUNTRY = 'country'
PRICE = 'price'
NUM_LIKES = 'num_likes'
CREATED_AT = 'created_at'

VALID_TRANSACTION_TYPES = {'free', 'sell'}

SAMPLE_LISTING = {
    TITLE: 'Textbook - Intro to CS',
    DESCRIPTION: 'Like new, barely used.',
    IMAGES: [],
    TRANSACTION_TYPE: 'sell',
    OWNER: 'student@nyu.edu',
    CITY: 'New York',
    STATE: 'NY',
    COUNTRY: 'USA',
    PRICE: 25.00,
    NUM_LIKES: 0,
}

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
    listings = dbc.read(LISTING_COLLECTION, no_id=False)
    for listing in listings:
        key = listing[dbc.MONGO_ID]
        cache[key] = listing


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


def _validate_listing(listing: dict) -> None:
    if not isinstance(listing, dict):
        raise ValueError("Listing must be a dictionary.")
    title = listing.get(TITLE)
    if TITLE not in listing or not title or not str(title).strip():
        raise ValueError("Listing must have a non-empty 'title'.")
    desc = listing.get(DESCRIPTION)
    if DESCRIPTION not in listing or not desc or not str(desc).strip():
        raise ValueError("Listing must have a non-empty 'description'.")
    if TRANSACTION_TYPE not in listing or not listing.get(TRANSACTION_TYPE):
        raise ValueError("Listing must have a 'transaction_type'.")
    tt = str(listing[TRANSACTION_TYPE]).strip().lower()
    if tt not in VALID_TRANSACTION_TYPES:
        valid_types = sorted(VALID_TRANSACTION_TYPES)
        got = repr(listing[TRANSACTION_TYPE])
        raise ValueError(
            f"transaction_type must be one of {valid_types}, "
            f"got {got}"
        )
    owner = listing.get(OWNER)
    if OWNER not in listing or not owner or not str(owner).strip():
        raise ValueError("Listing must have a non-empty 'owner'.")
    for fld in (CITY, STATE, COUNTRY):
        v = listing.get(fld)
        if fld not in listing or not v or not str(v).strip():
            raise ValueError(f"Listing must have a non-empty '{fld}'.")
    if IMAGES in listing and not isinstance(listing[IMAGES], list):
        raise ValueError("'images' must be a list of strings.")
    if IMAGES in listing and listing[IMAGES]:
        for i, url in enumerate(listing[IMAGES]):
            if not isinstance(url, str):
                url_type = type(url).__name__
                raise ValueError(
                    f"'images' must be a list of strings, "
                    f"got {url_type} at index {i}."
                )
    if PRICE in listing and listing[PRICE] is not None:
        try:
            float(listing[PRICE])
        except (TypeError, ValueError):
            raise ValueError("'price' must be a number or null.")
    if NUM_LIKES in listing and listing[NUM_LIKES] is not None:
        try:
            n = int(listing[NUM_LIKES])
            if n < 0:
                raise ValueError("'num_likes' must be a non-negative integer.")
        except TypeError:
            raise ValueError("'num_likes' must be a non-negative integer.")


def _validate_listing_update(update_dict: dict) -> None:
    """Validate only the fields present in an update payload."""
    if not update_dict or not isinstance(update_dict, dict):
        raise ValueError("Update must be a non-empty dictionary.")
    if TITLE in update_dict:
        t = update_dict[TITLE]
        if not t or not str(t).strip():
            raise ValueError("'title' must be non-empty.")
    if DESCRIPTION in update_dict:
        d = update_dict[DESCRIPTION]
        if not d or not str(d).strip():
            raise ValueError("'description' must be non-empty.")
    if TRANSACTION_TYPE in update_dict:
        tt = str(update_dict[TRANSACTION_TYPE]).strip().lower()
        if tt not in VALID_TRANSACTION_TYPES:
            raise ValueError(
                f"transaction_type must be one of "
                f"{sorted(VALID_TRANSACTION_TYPES)}, got "
                f"{repr(update_dict[TRANSACTION_TYPE])}"
            )
    for fld in (CITY, STATE, COUNTRY):
        if fld in update_dict:
            v = update_dict[fld]
            if v is None or not str(v).strip():
                raise ValueError(f"'{fld}' must be non-empty.")
    if PRICE in update_dict and update_dict[PRICE] is not None:
        try:
            float(update_dict[PRICE])
        except (TypeError, ValueError):
            raise ValueError("'price' must be a number or null.")
    if NUM_LIKES in update_dict and update_dict[NUM_LIKES] is not None:
        try:
            n = int(update_dict[NUM_LIKES])
            if n < 0:
                raise ValueError("'num_likes' must be a non-negative integer.")
        except TypeError:
            raise ValueError("'num_likes' must be a non-negative integer.")


LISTING_UPDATE_ALLOWED = {
    TITLE,
    DESCRIPTION,
    TRANSACTION_TYPE,
    CITY,
    STATE,
    COUNTRY,
    PRICE,
    NUM_LIKES,
}


@needs_cache
def update(listing_id: str, update_dict: dict) -> dict:
    """
    Update a listing by its MongoDB _id.
    Allowed fields: title, description, transaction_type,
    city, state, country, price, num_likes. Returns the updated listing.
    """
    if not isinstance(listing_id, str):
        raise ValueError(
            f"Listing ID must be a string, got {type(listing_id)}"
        )
    try:
        obj_id = ObjectId(listing_id)
    except Exception:
        raise ValueError(f"Invalid listing ID format: {listing_id}")
    allowed = {
        k: update_dict[k]
        for k in update_dict
        if k in LISTING_UPDATE_ALLOWED
    }
    if not allowed:
        raise ValueError(
            "Update must contain at least one allowed field: "
            "title, description, images, transaction_type, owner, "
            "city, state, country, price, num_likes."
        )
    _validate_listing_update(allowed)
    result = dbc.update(LISTING_COLLECTION, {dbc.MONGO_ID: obj_id}, allowed)
    if result.matched_count < 1:
        raise ValueError(f"Listing not found: {listing_id}")
    load_cache()
    return cache.get(listing_id, {})


@needs_cache
def num_listings() -> int:
    return len(cache)


@needs_cache
def create(listing: dict, reload=True) -> str:
    _validate_listing(listing)
    doc = dict(listing)
    if IMAGES not in doc or doc[IMAGES] is None:
        doc[IMAGES] = []
    if PRICE not in doc:
        doc[PRICE] = None
    if NUM_LIKES not in doc or doc[NUM_LIKES] is None:
        doc[NUM_LIKES] = 0
    doc[CREATED_AT] = datetime.now(timezone.utc).isoformat()
    rec_id = dbc.create(LISTING_COLLECTION, doc)
    if reload:
        load_cache()
    return rec_id


def delete(listing_id: str) -> bool:
    if not isinstance(listing_id, str):
        id_type = type(listing_id)
        raise ValueError(f"Listing ID must be a string, got {id_type}")
    try:
        obj_id = ObjectId(listing_id)
    except Exception:
        raise ValueError(f'Invalid listing ID format: {listing_id}')
    ret = dbc.delete(LISTING_COLLECTION, {dbc.MONGO_ID: obj_id})
    if ret < 1:
        raise ValueError(f'Listing not found: {listing_id}')
    load_cache()
    return ret > 0


@needs_cache
def read() -> dict:
    return cache


@needs_cache
def search_listings_by_title(search_term: str) -> dict:
    """
    Search for listings by title (case-insensitive partial match).
    Args:
        search_term: The term to search for in listing titles
    Returns:
        dict: Dictionary of listings matching the search term (keyed by _id)
    Raises:
        ValueError: If search_term is not a string or is empty
    """
    if not isinstance(search_term, str):
        raise ValueError(
            f'Search term must be a string, got {type(search_term)}'
        )
    if not search_term.strip():
        raise ValueError('Search term cannot be empty')
    search_lower = search_term.lower().strip()
    matching = {}
    for key, listing_data in cache.items():
        if search_lower in (listing_data.get(TITLE) or '').lower():
            matching[key] = listing_data
    return matching


@needs_cache
def search_listings_by_owner(owner: str) -> dict:
    """
    Return all listings that belong to a specific owner/username.
    Match is case-insensitive exact match on the owner field.
    """
    if not isinstance(owner, str):
        raise ValueError(f'Owner must be a string, got {type(owner)}')
    owner_lower = owner.strip().lower()
    if not owner_lower:
        raise ValueError('Owner cannot be empty')
    matching = {}
    for key, listing_data in cache.items():
        listing_owner = (listing_data.get(OWNER) or '').strip().lower()
        if listing_owner == owner_lower:
            matching[key] = listing_data
    return matching


def main():
    print(read())


if __name__ == '__main__':
    main()
