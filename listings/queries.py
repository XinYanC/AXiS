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
MEETUP_LOCATION = 'meetup_location'
PRICE = 'price'
CREATED_AT = 'created_at'

VALID_TRANSACTION_TYPES = {'buy', 'sell', 'donation', 'pickup', 'drop-off'}

SAMPLE_LISTING = {
    TITLE: 'Textbook - Intro to CS',
    DESCRIPTION: 'Like new, barely used.',
    IMAGES: [],
    TRANSACTION_TYPE: 'sell',
    OWNER: 'student@nyu.edu',
    MEETUP_LOCATION: 'Bobst Library',
    PRICE: 25.00,
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
    loc = listing.get(MEETUP_LOCATION)
    if MEETUP_LOCATION not in listing or not loc or not str(loc).strip():
        raise ValueError("Listing must have a non-empty 'meetup_location'.")
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


def main():
    print(read())


if __name__ == '__main__':
    main()
