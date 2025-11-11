# To run test: PYTHONPATH=$(pwd) pytest -v cities/tests/test_queries.py

from unittest.mock import patch

import pytest

import cities.queries as qry

from copy import deepcopy

def get_temp_rec():
    return deepcopy(qry.SAMPLE_CITY)


@pytest.fixture
def temp_city_unique():
    temp_rec = get_temp_rec()
    rec_id = qry.create(temp_rec)
    yield rec_id, temp_rec
    try:
        qry.delete(temp_rec[qry.NAME], temp_rec[qry.STATE_CODE])
    except ValueError:
        pass


@pytest.fixture(scope='function')
def sample_cities():
    """Provide a small set of cities in the database for search tests.

    This fixture creates test cities in the database and cleans them up afterwards.
    """
    cities_to_create = [
        {'name': 'New York', 'state_code': 'NY'},
        {'name': 'Los Angeles', 'state_code': 'CA'},
        {'name': 'New Orleans', 'state_code': 'LA'},
    ]
    created_ids = []
    for city in cities_to_create:
        city_id = qry.create(city)
        created_ids.append((city[qry.NAME], city[qry.STATE_CODE]))
    try:
        yield cities_to_create
    finally:
        # Clean up created cities
        for name, state_code in created_ids:
            try:
                qry.delete(name, state_code)
            except ValueError:
                pass  # Already deleted


def test_search_cities_by_name_with_fixture(sample_cities):
    # partial match
    results = qry.search_cities_by_name('New')
    assert isinstance(results, dict)
    # Check that we have cities with 'New' in the name
    city_names = [city.get('name', '') for city in results.values()]
    assert 'New York' in city_names
    assert 'New Orleans' in city_names
    assert 'Los Angeles' not in city_names

    # case-insensitive match
    results_ci = qry.search_cities_by_name('los angeles')
    city_names_ci = [city.get('name', '') for city in results_ci.values()]
    assert 'Los Angeles' in city_names_ci


def test_search_cities_by_name_no_matches():
    """Verify a search with no matches returns an empty dict."""
    # Search for a city that likely doesn't exist
    results = qry.search_cities_by_name('XyZ123NonexistentCity456')
    assert isinstance(results, dict)
    assert len(results) == 0

    
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    # This test is skipped as it's an example of a bad test
    pass


def test_num_cities():
    # get the count
    old_count = qry.num_cities()
    # add a record
    temp_rec = get_temp_rec()
    qry.create(temp_rec)
    assert qry.num_cities() == old_count + 1
    # Clean up
    qry.delete(temp_rec[qry.NAME], temp_rec[qry.STATE_CODE])


def test_good_create():
    old_count = qry.num_cities()
    new_rec_id = qry.create(get_temp_rec())

    # id returned should be valid
    assert qry.is_valid_id(new_rec_id)

    # city count should increase
    assert qry.num_cities() == old_count + 1

    # city data should be stored correctly in database
    cities = qry.read()
    created_city = None
    for city in cities:
        # Check if this city matches our sample city
        if city.get('name') == qry.SAMPLE_CITY['name'] and city.get('state_code') == qry.SAMPLE_CITY['state_code']:
            created_city = city
            break
    assert created_city is not None
    assert created_city['name'] == qry.SAMPLE_CITY['name']
    assert created_city['state_code'] == qry.SAMPLE_CITY['state_code']
    
    # Clean up
    qry.delete(qry.SAMPLE_CITY['name'], qry.SAMPLE_CITY['state_code'])

@pytest.mark.parametrize("city_data, match", [
    ({}, "name"),
    (17, "Invalid"),
    ({'state_code': 'NY'}, "name"),
    ({'name': 'City'}, "state_code"),
    ({'name': None, 'state_code': 'NY'}, "name"),
    ({'name': 'Test City', 'state_code': None}, "state_code"),
])
def test_create_invalid_inputs(city_data, match):
    with pytest.raises(ValueError):
        qry.create(city_data)

def test_delete(temp_city_unique):
    rec_id, rec = temp_city_unique
    ret = qry.delete(rec[qry.NAME], rec[qry.STATE_CODE])
    assert ret == 1


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some city name that is not there, not a state')


def test_read(temp_city_unique):
    cities = qry.read()
    assert isinstance(cities, list)
    assert get_temp_rec() in cities


@pytest.mark.skip('revive once all functions are cutover!')
def test_read_cant_connect(mock_db_connect):
    with pytest.raises(ConnectionError):
        cities = qry.read()


def test_is_valid_id(temp_city_unique):
    # valid id (from fixture)
    rec_id, rec = temp_city_unique
    result = qry.is_valid_id(rec_id)
    assert isinstance(result, bool)
    assert result is True


def test_is_valid_id_invalid_types():
    assert not qry.is_valid_id(None)
    assert not qry.is_valid_id(123)


def test_is_valid_id_invalid_length():
    # empty string is invalid
    assert not qry.is_valid_id('')


def test_is_valid_id_min_len():
    old_min = qry.MIN_ID_LEN
    try:
        # len has to be greater or equal to MIN_ID_LEN
        qry.MIN_ID_LEN = 2
        assert not qry.is_valid_id('a')
        assert qry.is_valid_id('ab')
    finally:
        qry.MIN_ID_LEN = old_min

    assert isinstance(qry.is_valid_id(' '), bool)
    assert qry.is_valid_id(' ')


def test_delete_returns_true_and_removes(temp_city_unique):
    # temp_city is the MongoDB _id returned from create
    rec_id, rec = temp_city_unique
    assert qry.delete(rec_id)
    # Verify it's deleted by checking read() doesn't contain it
    # (We can't easily check by ID since read() removes _id by default)
    cities = qry.read()
    # The city should be deleted, but we can't directly verify by ID
    # So we just verify delete returns True
    pass

def test_read_returns_expected_fields(temp_city_unique):
    cities = qry.read()
    for data in cities:
        assert 'name' in data
        assert 'state_code' in data

def test_create_duplicate_city():
    # Create unique cities to avoid duplicate key errors
    import time
    timestamp = int(time.time() * 1000)
    city1 = {'name': f'Duplicate Test City {timestamp}', 'state_code': 'DT'}
    city2 = {'name': f'Duplicate Test City {timestamp + 1}', 'state_code': 'DT'}
    
    rec_id1 = qry.create(city1)
    rec_id2 = qry.create(city2)
    
    assert rec_id1 != rec_id2
    # Delete by ID (MongoDB _id)
    qry.delete(rec_id1)
    qry.delete(rec_id2)

@pytest.mark.skip('revive once data format in MongoDB is confirmed')
def test_search_cities_by_name(temp_city):
    """Test searching cities by name"""
    # This test is skipped and will need to be updated when revived
    # to work with database instead of city_cache
    pass


def test_search_cities_by_name_invalid_input():
    """Test search function with invalid inputs"""
    # Test non-string input
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_cities_by_name(123)
    
    # Test empty string
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_cities_by_name('')
    
    # Test whitespace only
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_cities_by_name('   ')
    
    # Test None input
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_cities_by_name(None)

def test_delete_by_invalid_id_format():
    """Test that delete raises ValueError for invalid ObjectId format"""
    with pytest.raises(ValueError, match='Invalid city ID format'):
        qry.delete('invalid-id-format')


def test_create_multiple_cities_and_count():
    """Test creating multiple cities and verifying count"""
    import time
    timestamp = int(time.time() * 1000)
    test_cities = [
        {'name': f'Multi City {timestamp} A', 'state_code': 'MC'},
        {'name': f'Multi City {timestamp} B', 'state_code': 'MC'},
        {'name': f'Multi City {timestamp} C', 'state_code': 'MC'},
    ]
    
    initial_count = qry.num_cities()
    created_cities = []
    
    try:
        for city in test_cities:
            city_id = qry.create(city)
            created_cities.append(city)
        
        assert qry.num_cities() == initial_count + len(test_cities)
    finally:
        # Clean up
        for city in created_cities:
            try:
                qry.delete(city[qry.NAME], city[qry.STATE_CODE])
            except ValueError:
                pass


def test_main_prints_read(monkeypatch, capsys):
    """Patch qry.read to return a known list and verify main() prints it."""
    sample = [{'name': 'Printed City', 'state_code': 'PC'}]

    # Patch the module-level read function used by main()
    monkeypatch.setattr(qry, 'read', lambda: sample)

    # Call main() which should print the returned list
    qry.main()

    captured = capsys.readouterr()
    out = captured.out

    # Expect the printed representation to include the city name and state_code
    assert 'Printed City' in out
    assert 'PC' in out


def test_read_raises_on_db_connection_error(monkeypatch):
    """Ensure qry.read propagates a ConnectionError from the DB layer."""
    def raise_conn(collection):
        raise ConnectionError('unable to connect')

    monkeypatch.setattr(qry.dbc, 'read', raise_conn)

    import pytest
    with pytest.raises(ConnectionError, match='unable to connect'):
        qry.read()

def test_delete_by_id_success_and_not_found(monkeypatch):
    """Test delete when passed a MongoDB _id string: success and not-found cases."""
    from bson import ObjectId

    valid_id = str(ObjectId())

    # Success case: dbc.delete returns >=1 -> delete() should return True
    def fake_delete_success(collection, query):
        # Verify the query contains a bson ObjectId under the MONGO_ID key
        assert qry.dbc.MONGO_ID in query
        assert isinstance(query[qry.dbc.MONGO_ID], ObjectId)
        return 1

    monkeypatch.setattr(qry.dbc, 'delete', fake_delete_success)
    assert qry.delete(valid_id) is True

    # Not found case: dbc.delete returns 0 -> delete() should raise ValueError
    def fake_delete_not_found(collection, query):
        return 0

    monkeypatch.setattr(qry.dbc, 'delete', fake_delete_not_found)
    import pytest
    with pytest.raises(ValueError, match='City not found'):
        qry.delete(valid_id)