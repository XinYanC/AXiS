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
            qry.MEETUP_LOCATION: 'Library',
        },
        {
            qry.TITLE: 'Desk Lamp',
            qry.DESCRIPTION: 'LED, good condition',
            qry.TRANSACTION_TYPE: 'sell',
            qry.OWNER: 'b@nyu.edu',
            qry.MEETUP_LOCATION: 'Dorm A',
        },
        {
            qry.TITLE: 'Free Chair',
            qry.DESCRIPTION: 'Donation',
            qry.TRANSACTION_TYPE: 'donation',
            qry.OWNER: 'c@nyu.edu',
            qry.MEETUP_LOCATION: 'Lobby',
        },
    ]
    created_ids = []
    qry.clear_cache()
    for listing in listings_to_create:
        rec_id = qry.create(listing)
        created_ids.append(rec_id)
    try:
        yield listings_to_create
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
    finally:
        safe_delete(new_rec_id)


@pytest.mark.parametrize("listing_data, match", [
    ({}, "title"),
    (17, "dictionary"),
    ({qry.TITLE: 'Only title'}, "description"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B'}, "transaction_type"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B', qry.TRANSACTION_TYPE: 'invalid'}, "one of"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B', qry.TRANSACTION_TYPE: 'sell'}, "owner"),
    ({qry.TITLE: 'A', qry.DESCRIPTION: 'B', qry.TRANSACTION_TYPE: 'sell', qry.OWNER: 'x@nyu.edu'}, "meetup_location"),
])
def test_create_invalid_inputs(listing_data, match):
    with pytest.raises(ValueError, match=match):
        qry.create(listing_data)


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
    listings = qry.read()
    for data in listings.values():
        assert qry.TITLE in data
        assert qry.DESCRIPTION in data
        assert qry.TRANSACTION_TYPE in data
        assert qry.OWNER in data
        assert qry.MEETUP_LOCATION in data
        assert qry.CREATED_AT in data


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
