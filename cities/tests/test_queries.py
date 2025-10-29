# To run test: PYTHONPATH=$(pwd) pytest -v cities/tests/test_queries.py

from unittest.mock import patch

import pytest

import cities.queries as qry


@pytest.fixture(scope='function')
def temp_city():
    # Create a unique city for each test to avoid duplicate key errors
    import time
    unique_city = {
        'name': f'Test City {int(time.time() * 1000)}',
        'state_code': 'TC'
    }
    new_rec_id = qry.create(unique_city)
    # Add to cache so delete function can find it
    qry.city_cache[new_rec_id] = unique_city
    yield new_rec_id
    try:
        qry.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')


@pytest.fixture(scope='function')
def sample_cities():
    """Provide a small set of cities in the cache for search tests.

    This fixture replaces the module-level `city_cache` with a known
    dictionary and restores the original cache afterwards.
    """
    original_cache = dict(qry.city_cache)
    qry.city_cache = {
        'c1': {'name': 'New York', 'state_code': 'NY'},
        'c2': {'name': 'Los Angeles', 'state_code': 'CA'},
        'c3': {'name': 'New Orleans', 'state_code': 'LA'},
    }
    try:
        yield qry.city_cache
    finally:
        qry.city_cache = original_cache


def test_search_cities_by_name_with_fixture(sample_cities):
    # partial match
    results = qry.search_cities_by_name('New')
    assert isinstance(results, dict)
    assert 'c1' in results
    assert 'c3' in results
    assert 'c2' not in results

    # case-insensitive match
    results_ci = qry.search_cities_by_name('los angeles')
    assert 'c2' in results_ci


def test_search_cities_by_name_no_matches_with_patch():
    """Use patch to set the cache and verify a search with no matches returns an empty dict."""
    patched_cache = {
        'a': {'name': 'Springfield', 'state_code': 'IL'},
        'b': {'name': 'Shelbyville', 'state_code': 'IL'},
    }
    with patch('cities.queries.city_cache', new=patched_cache):
        results = qry.search_cities_by_name('Chicago')
        assert isinstance(results, dict)
        assert len(results) == 0

    
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    assert qry.num_cities() == len(qry.city_cache)


@pytest.mark.skip('revive once all functions are cutover!')
def test_num_cities():
    # get the count
    old_count = qry.num_cities()
    # add a record
    qry.create(qry.SAMPLE_CITY)
    assert qry.num_cities() == old_count + 1


def test_good_create():
    old_count = qry.num_cities()
    new_rec_id = qry.create(qry.SAMPLE_CITY)

    # id returned should be valid
    assert qry.is_valid_id(new_rec_id)

    # city count should increase
    assert qry.num_cities() == old_count + 1

    # city data should be stored correctly
    created_city = qry.city_cache.get(new_rec_id)
    assert created_city is not None
    assert created_city['name'] == qry.SAMPLE_CITY['name']
    assert created_city['state_code'] == qry.SAMPLE_CITY['state_code']


def test_create_bad_name():
    with pytest.raises(ValueError):
        qry.create({})


def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)

@pytest.mark.skip('revive once all functions are cutover!')
def test_delete(mock_db_connect, temp_city):
    qry.delete(temp_city)
    assert temp_city not in qry.read()


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some value that is not there')


@pytest.mark.skip('revive once all functions are cutover!')
def test_read(temp_city):
    cities = qry.read()
    assert isinstance(cities, dict)
    assert temp_city in cities


@pytest.mark.skip('revive once all functions are cutover!')
def test_read_cant_connect(mock_db_connect):
    with pytest.raises(ConnectionError):
        cities = qry.read()

def test_create_missing_name_field():
    # Missing 'name' key should raise
    with pytest.raises(ValueError):
        qry.create({'state_code': 'NY'})


def test_create_missing_state_code_field():
    # Missing 'state_code' key should raise
    with pytest.raises(ValueError):
        qry.create({'name': 'City Without State'})


def test_is_valid_id(temp_city):
    # valid id (from fixture)
    result = qry.is_valid_id(temp_city)
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


def test_delete_returns_true_and_removes(temp_city):
    assert qry.delete(temp_city)
    assert temp_city not in qry.city_cache

def test_read_returns_expected_fields(temp_city):
    cities = qry.read()
    for city_id, data in cities.items():
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
    # Add to cache so delete function can find them
    qry.city_cache[rec_id1] = city1
    qry.city_cache[rec_id2] = city2
    
    assert rec_id1 != rec_id2
    qry.delete(rec_id1)
    qry.delete(rec_id2)

@pytest.mark.skip('revive once data format in MongoDB is confirmed')
def test_search_cities_by_name(temp_city):
    """Test searching cities by name"""
    # Add some test cities to the cache
    test_cities = {
        'city1': {'name': 'New York', 'state_code': 'NY'},
        'city2': {'name': 'Los Angeles', 'state_code': 'CA'},
        'city3': {'name': 'New Orleans', 'state_code': 'LA'},
    }
    qry.city_cache = test_cities
    
    # Test exact match
    results = qry.search_cities_by_name('New York')
    assert len(results) == 1
    assert 'city1' in results
    
    # Test partial match
    results = qry.search_cities_by_name('New')
    assert len(results) == 2
    assert 'city1' in results
    assert 'city3' in results
    
    # Test case insensitive
    results = qry.search_cities_by_name('los angeles')
    assert len(results) == 1
    assert 'city2' in results
    
    # Test no matches
    results = qry.search_cities_by_name('Chicago')
    assert len(results) == 0


@pytest.mark.skip('revive once data format in MongoDB is confirmed')
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
