# To run test: PYTHONPATH=$(pwd) pytest -v listings/tests/test_queries.py

from copy import deepcopy
from unittest.mock import patch

import pytest

import listings.queries as qry


def safe_delete(listing_id):
    try:
        qry.delete(listing_id)
    except ValueError:
        pass


def get_temp_rec():
    return deepcopy(qry.SAMPLE_LISTING)


@pytest.fixture
def temp_listing_unique():
    """Create a temporary listing for testing and clean up after."""
    temp_rec = get_temp_rec()
    qry.clear_cache()
    rec_id = qry.create(temp_rec)
    yield rec_id, temp_rec
    safe_delete(rec_id)


@pytest.fixture(scope='function')
def sample_listings():
    """Provide a small set of listings in the database for search tests."""
    listings_to_create = [
        {
            qry.TITLE: 'Calculus Textbook',
            qry.DESCRIPTION: 'Stewart 9th ed.',
            qry.TRANSACTION_TYPE: 'sell',
            qry.OWNER: 'a@nyu.edu',
            qry.CITY: 'New York',
            qry.STATE: 'NY',
            qry.COUNTRY: 'USA',
        },
        {
            qry.TITLE: 'Desk Lamp',
            qry.DESCRIPTION: 'LED, good condition',
            qry.TRANSACTION_TYPE: 'sell',
            qry.OWNER: 'b@nyu.edu',
            qry.CITY: 'Brooklyn',
            qry.STATE: 'NY',
            qry.COUNTRY: 'USA',
        },
        {
            qry.TITLE: 'Free Chair',
            qry.DESCRIPTION: 'Donation',
            qry.TRANSACTION_TYPE: 'free',
            qry.OWNER: 'c@nyu.edu',
            qry.CITY: 'Queens',
            qry.STATE: 'NY',
            qry.COUNTRY: 'USA',
        },
    ]
    created_ids = []
    qry.clear_cache()
    for listing in listings_to_create:
        rec_id = qry.create(listing)
        created_ids.append(rec_id)
    try:
        yield {
            'listings': listings_to_create,
            'ids': frozenset(created_ids),
        }
    finally:
        for rec_id in created_ids:
            safe_delete(rec_id)


def test_num_listings(temp_listing_unique):
    """Test that num_listings returns correct count."""
    rec_id, _ = temp_listing_unique
    count = qry.num_listings()
    assert count >= 1
    safe_delete(rec_id)
    qry.clear_cache()
    assert qry.num_listings() == count - 1


def test_good_create():
    """Test creating a listing with valid data."""
    temp_rec = get_temp_rec()
    qry.clear_cache()
    old_count = qry.num_listings()
    new_rec_id = qry.create(temp_rec)
    try:
        assert qry.is_valid_id(new_rec_id)
        assert qry.num_listings() == old_count + 1
        listings = qry.read()
        assert new_rec_id in listings
        created = listings[new_rec_id]
        assert created[qry.TITLE] == qry.SAMPLE_LISTING[qry.TITLE]
        assert created[qry.DESCRIPTION] == qry.SAMPLE_LISTING[qry.DESCRIPTION]
        assert created[qry.TRANSACTION_TYPE] == qry.SAMPLE_LISTING[qry.TRANSACTION_TYPE]
        assert created[qry.OWNER] == qry.SAMPLE_LISTING[qry.OWNER]
        assert qry.CREATED_AT in created
        assert created.get(qry.NUM_LIKES, 0) == qry.SAMPLE_LISTING.get(
            qry.NUM_LIKES, 0
        )
    finally:
        safe_delete(new_rec_id)


@pytest.mark.parametrize("listing_data, match", [
    ({}, "title"),
    (17, "dictionary"),
    ({qry.TITLE: 'Only title'}, "description"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B'}, "transaction_type"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B', qry.TRANSACTION_TYPE: 'invalid'}, "one of"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B', qry.TRANSACTION_TYPE: 'sell'}, "owner"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B', qry.TRANSACTION_TYPE: 'sell', qry.OWNER: 'x@nyu.edu'}, "city"),
])
def test_create_invalid_inputs(listing_data, match):
    with pytest.raises(ValueError, match=match):
        qry.create(listing_data)

@pytest.mark.parametrize("bad_type", [
    'swap', 'trade', 'rent', 'buy', 'donation', 'pickup', 'drop-off', '', '  ', None, 123,
])
def test_create_invalid_transaction_type(bad_type):
    listing = {
        qry.TITLE: 'Test Item',
        qry.DESCRIPTION: 'A description',
        qry.TRANSACTION_TYPE: bad_type,
        qry.OWNER: 'x@nyu.edu',
        qry.CITY: 'NYC',
        qry.STATE: 'NY',
        qry.COUNTRY: 'USA',
    }
    with pytest.raises(ValueError):
        qry.create(listing)


@pytest.mark.parametrize("valid_type", list(qry.VALID_TRANSACTION_TYPES))
def test_create_all_valid_transaction_types(valid_type):
    listing = {
        qry.TITLE: 'Test Item',
        qry.DESCRIPTION: 'A description',
        qry.TRANSACTION_TYPE: valid_type,
        qry.OWNER: 'x@nyu.edu',
        qry.CITY: 'NYC',
        qry.STATE: 'NY',
        qry.COUNTRY: 'USA',
    }
    qry.clear_cache()
    rec_id = qry.create(listing)
    try:
        assert qry.is_valid_id(rec_id)
    finally:
        safe_delete(rec_id)


def test_delete(temp_listing_unique):
    rec_id, _ = temp_listing_unique
    ret = qry.delete(rec_id)
    assert ret is True


def test_delete_not_there():
    with pytest.raises(ValueError, match='Invalid listing ID format'):
        qry.delete('not-a-valid-object-id')


def test_delete_by_id_success_and_not_found():
    """Test delete when passed an id: success and not-found cases."""
    with patch('listings.queries.dbc.delete', return_value=1) as fake_del:
        from bson import ObjectId
        valid_id = str(ObjectId())
        assert qry.delete(valid_id) is True
        fake_del.assert_called()
    with patch('listings.queries.dbc.delete', return_value=0):
        from bson import ObjectId
        valid_id = str(ObjectId())
        with pytest.raises(ValueError, match='Listing not found'):
            qry.delete(valid_id)


def test_read(temp_listing_unique):
    listings = qry.read()
    assert isinstance(listings, dict)
    rec_id, _ = temp_listing_unique
    assert rec_id in listings


def test_read_returns_expected_fields(temp_listing_unique):
    rec_id, _ = temp_listing_unique
    listings = qry.read()
    assert rec_id in listings
    data = listings[rec_id]
    assert qry.TITLE in data
    assert qry.DESCRIPTION in data
    assert qry.TRANSACTION_TYPE in data
    assert qry.OWNER in data
    assert qry.CITY in data
    assert qry.STATE in data
    assert qry.COUNTRY in data
    assert qry.CREATED_AT in data
    assert qry.NUM_LIKES in data


def test_is_valid_id(temp_listing_unique):
    rec_id, _ = temp_listing_unique
    assert qry.is_valid_id(rec_id) is True


def test_is_valid_id_invalid_types():
    assert not qry.is_valid_id(None)
    assert not qry.is_valid_id(123)


def test_is_valid_id_invalid_length():
    assert not qry.is_valid_id('')


def test_search_listings_by_title_with_fixture(sample_listings):
    results = qry.search_listings_by_title('Textbook')
    assert isinstance(results, dict)
    titles = [d.get(qry.TITLE, '') for d in results.values()]
    assert 'Calculus Textbook' in titles
    results = qry.search_listings_by_title('desk')
    titles = [d.get(qry.TITLE, '') for d in results.values()]
    assert 'Desk Lamp' in titles


def test_search_listings_by_title_no_matches():
    results = qry.search_listings_by_title('XyZ123NonexistentListing456')
    assert isinstance(results, dict)
    assert len(results) == 0


def test_search_listings_by_title_invalid_input():
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_listings_by_title(123)
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_listings_by_title('')
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_listings_by_title('   ')
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_listings_by_title(None)


def test_search_listings_by_owner_returns_all_matches(monkeypatch):
    sample_cache = {
        'id1': {qry.TITLE: 'Book A', qry.OWNER: 'testuser'},
        'id2': {qry.TITLE: 'Book B', qry.OWNER: 'TestUser'},
        'id3': {qry.TITLE: 'Book C', qry.OWNER: 'otheruser'},
    }
    monkeypatch.setattr(qry, 'cache', sample_cache)

    results = qry.search_listings_by_owner('testuser')

    assert isinstance(results, dict)
    assert set(results.keys()) == {'id1', 'id2'}
    assert all(
        (listing.get(qry.OWNER) or '').lower() == 'testuser'
        for listing in results.values()
    )


def test_search_listings_by_owner_invalid_input(monkeypatch):
    monkeypatch.setattr(qry, 'cache', {'dummy': {}})

    with pytest.raises(ValueError, match='Owner must be a string'):
        qry.search_listings_by_owner(123)
    with pytest.raises(ValueError, match='Owner cannot be empty'):
        qry.search_listings_by_owner('   ')


# ---- read_paginated ---------------------------------------------------

@pytest.fixture
def paginated_cache(monkeypatch):
    """A small in-memory cache + a no-op load_cache for paginated tests."""
    sample = {
        'id1': {
            qry.TITLE: 'A', qry.OWNER: 'a@nyu.edu',
            qry.STATUS: 'available', qry.CREATED_AT: '2026-01-01',
            qry.PRICE: 10, qry.NUM_LIKES: 1,
        },
        'id2': {
            qry.TITLE: 'B', qry.OWNER: 'b@nyu.edu',
            qry.STATUS: 'available', qry.CREATED_AT: '2026-02-01',
            qry.PRICE: 20, qry.NUM_LIKES: 2,
        },
        'id3': {
            qry.TITLE: 'C', qry.OWNER: 'a@nyu.edu',
            qry.STATUS: 'sold', qry.CREATED_AT: '2026-03-01',
            qry.PRICE: 30, qry.NUM_LIKES: 3,
        },
        'id4': {
            qry.TITLE: 'D', qry.OWNER: 'a@nyu.edu',
            qry.STATUS: 'available', qry.CREATED_AT: '2026-04-01',
            qry.PRICE: 5, qry.NUM_LIKES: 0,
        },
    }
    monkeypatch.setattr(qry, 'cache', sample)
    monkeypatch.setattr(qry, 'load_cache', lambda: None)
    return sample


def test_read_paginated_default_sort_desc_created_at(paginated_cache):
    res = qry.read_paginated()
    assert res['total'] == 4
    assert res['page'] == 1
    assert res['page_size'] == qry.PAGE_SIZE_DEFAULT
    assert res['has_next'] is False
    titles = [it[qry.TITLE] for it in res['items']]
    assert titles == ['D', 'C', 'B', 'A']  # newest first


def test_read_paginated_status_filter(paginated_cache):
    res = qry.read_paginated(status='available')
    assert res['total'] == 3
    assert all(it[qry.STATUS] == 'available' for it in res['items'])


def test_read_paginated_owner_filter_case_insensitive(paginated_cache):
    res = qry.read_paginated(owner='A@NYU.EDU')
    assert res['total'] == 3
    assert all(it[qry.OWNER] == 'a@nyu.edu' for it in res['items'])


def test_read_paginated_pagination_boundaries(paginated_cache):
    p1 = qry.read_paginated(page=1, page_size=2)
    p2 = qry.read_paginated(page=2, page_size=2)
    p3 = qry.read_paginated(page=3, page_size=2)
    assert p1['total'] == p2['total'] == p3['total'] == 4
    assert p1['has_next'] is True
    assert p2['has_next'] is False
    assert p3['items'] == []
    # No overlap between page 1 and page 2.
    p1_titles = {it[qry.TITLE] for it in p1['items']}
    p2_titles = {it[qry.TITLE] for it in p2['items']}
    assert p1_titles.isdisjoint(p2_titles)


def test_read_paginated_page_size_capped(paginated_cache):
    res = qry.read_paginated(page_size=10_000)
    assert res['page_size'] == qry.PAGE_SIZE_MAX


def test_read_paginated_sort_ascending_price(paginated_cache):
    res = qry.read_paginated(sort='price')
    prices = [it[qry.PRICE] for it in res['items']]
    assert prices == sorted(prices)


def test_read_paginated_invalid_inputs(paginated_cache):
    with pytest.raises(ValueError, match="'page'"):
        qry.read_paginated(page=0)
    with pytest.raises(ValueError, match="'page_size'"):
        qry.read_paginated(page_size=0)
    with pytest.raises(ValueError, match='sort must be one of'):
        qry.read_paginated(sort='not_a_field')


def test_read_paginated_combined_filter_and_sort(paginated_cache):
    res = qry.read_paginated(
        status='available', owner='a@nyu.edu', sort='-num_likes',
    )
    titles = [it[qry.TITLE] for it in res['items']]
    # only id1 (likes=1) and id4 (likes=0) match; -num_likes => id1 first
    assert titles == ['A', 'D']


def test_create_with_price_and_images():
    temp_rec = get_temp_rec()
    temp_rec[qry.PRICE] = 10.5
    temp_rec[qry.IMAGES] = ['https://example.com/1.jpg']
    qry.clear_cache()
    rec_id = qry.create(temp_rec)
    try:
        listings = qry.read()
        created = listings[rec_id]
        assert created[qry.PRICE] == 10.5
        assert created[qry.IMAGES] == ['https://example.com/1.jpg']
    finally:
        safe_delete(rec_id)


def test_create_with_num_likes():
    """Test creating a listing with num_likes and that it defaults to 0."""
    temp_rec = get_temp_rec()
    qry.clear_cache()
    rec_id = qry.create(temp_rec)
    try:
        listings = qry.read()
        created = listings[rec_id]
        assert created[qry.NUM_LIKES] == 0
    finally:
        safe_delete(rec_id)
    # Create with explicit num_likes
    temp_rec2 = get_temp_rec()
    temp_rec2[qry.OWNER] = 'other@nyu.edu'
    temp_rec2[qry.NUM_LIKES] = 5
    rec_id2 = qry.create(temp_rec2)
    try:
        listings = qry.read()
        created = listings[rec_id2]
        assert created[qry.NUM_LIKES] == 5
    finally:
        safe_delete(rec_id2)


@pytest.mark.parametrize("bad_num_likes", [-1])
def test_create_invalid_num_likes(bad_num_likes):
    """num_likes must be a non-negative integer."""
    listing = {
        qry.TITLE: 'Test Item',
        qry.DESCRIPTION: 'A description',
        qry.TRANSACTION_TYPE: 'sell',
        qry.OWNER: 'x@nyu.edu',
        qry.CITY: 'NYC',
        qry.STATE: 'NY',
        qry.COUNTRY: 'USA',
        qry.NUM_LIKES: bad_num_likes,
    }
    with pytest.raises(ValueError, match='num_likes'):
        qry.create(listing)


def test_create_sets_created_at():
    temp_rec = get_temp_rec()
    qry.clear_cache()
    rec_id = qry.create(temp_rec)
    try:
        listings = qry.read()
        created = listings[rec_id]
        assert qry.CREATED_AT in created
        assert isinstance(created[qry.CREATED_AT], str)
        assert 'T' in created[qry.CREATED_AT]
    finally:
        safe_delete(rec_id)


def test_main_prints_read(monkeypatch, capsys):
    sample = {'id1': {qry.TITLE: 'Test Listing', qry.OWNER: 'o@nyu.edu'}}
    monkeypatch.setattr(qry, 'read', lambda: sample)
    qry.main()
    captured = capsys.readouterr()
    assert 'Test Listing' in captured.out
    assert 'o@nyu.edu' in captured.out


def test_delete_rejects_non_string():
    with pytest.raises(ValueError, match='Listing ID must be a string'):
        qry.delete(123)


def test_update_by_id(temp_listing_unique):
    """Update listing by id; allowed fields are applied."""
    rec_id, rec = temp_listing_unique
    updated = qry.update(rec_id, {qry.TITLE: 'Updated Title', qry.PRICE: 99.0})
    assert updated.get(qry.TITLE) == 'Updated Title'
    assert updated.get(qry.PRICE) == 99.0
    assert rec_id in qry.read()
    assert qry.read()[rec_id][qry.TITLE] == 'Updated Title'


def test_update_partial(temp_listing_unique):
    """Update only one field (e.g. num_likes)."""
    rec_id, rec = temp_listing_unique
    updated = qry.update(rec_id, {qry.NUM_LIKES: 10})
    assert updated.get(qry.NUM_LIKES) == 10
    assert updated.get(qry.TITLE) == rec.get(qry.TITLE)


def test_update_invalid_listing_id():
    with pytest.raises(ValueError, match='Invalid listing ID format'):
        qry.update('not-valid-id', {qry.TITLE: 'X'})
