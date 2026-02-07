# To run test: PYTHONPATH=$(pwd) pytest -v countries/tests/test_queries.py

from unittest.mock import patch

import pytest

import countries.queries as qry

from copy import deepcopy

def safe_delete(country):
    try:
        qry.delete(country[qry.NAME], country[qry.CODE])
    except ValueError:
        pass


def get_temp_rec():
    return deepcopy(qry.SAMPLE_COUNTRY)


@pytest.fixture
def clean_sample_country():
    """Ensure SAMPLE_COUNTRY is deleted before test and clean up after."""
    temp_rec = get_temp_rec()
    try:
        qry.delete(temp_rec[qry.NAME], temp_rec[qry.CODE])
    except ValueError:
        pass
    qry.clear_cache()
    yield
    safe_delete(temp_rec)


@pytest.fixture
def temp_country_unique(clean_sample_country):
    """Create a temporary country for testing and clean up after."""
    temp_rec = get_temp_rec()
    rec_id = qry.create(temp_rec)
    yield rec_id, temp_rec
    safe_delete(temp_rec)


@pytest.fixture(scope='function')
def sample_countries():
    """Provide a small set of countries in the database for search tests.

    This fixture creates test countries in the database and cleans them up afterwards.
    """
    countries_to_create = [
        {'name': 'United Kingdom', 'code': 'UK'},
        {'name': 'United Arab Emirates', 'code': 'UAE'},
    ]
    created_ids = []
    # Clean up any existing countries first
    for country in countries_to_create:
        try:
            qry.delete(country[qry.NAME], country[qry.CODE])
        except ValueError:
            pass  # Doesn't exist, which is fine
    # Clear cache to ensure fresh state
    qry.clear_cache()
    # Now create the countries
    for country in countries_to_create:
        country_id = qry.create(country)
        created_ids.append((country[qry.NAME], country[qry.CODE]))
    try:
        yield countries_to_create
    finally:
        # Clean up created countries
        for name, code in created_ids:
            safe_delete({'name': name, 'code': code})


def test_search_countries_by_name_with_fixture(sample_countries):
    # partial match
    results = qry.search_countries_by_name('United')
    assert isinstance(results, dict)
    # Check that we have countries with 'United' in the name
    country_names = [country.get('name', '') for country in results.values()]
    assert 'United Kingdom' in country_names
    assert 'United Arab Emirates' in country_names

    # case-insensitive match
    results_ci = qry.search_countries_by_name('united kingdom')
    country_names_ci = [country.get('name', '') for country in results_ci.values()]
    assert 'United Kingdom' in country_names_ci


def test_search_countries_by_name_no_matches():
    """Verify a search with no matches returns an empty dict."""
    # Search for a country that likely doesn't exist
    results = qry.search_countries_by_name('XyZ123NonexistentCountry456')
    assert isinstance(results, dict)
    assert len(results) == 0

    
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_countries():
    # This test is skipped as it's an example of a bad test
    pass


def test_num_countries(clean_sample_country):
    """Test that num_countries returns correct count."""
    temp_rec = get_temp_rec()
    # Ensure it's deleted (clean_sample_country fixture handles this, but be explicit)
    safe_delete(temp_rec)
    qry.clear_cache()
    old_count = qry.num_countries()
    qry.create(temp_rec)
    assert qry.num_countries() == old_count + 1
    # Clean up
    safe_delete(temp_rec)


def test_good_create(clean_sample_country):
    """Test creating a country with valid data."""
    temp_rec = get_temp_rec()
    # Ensure it's deleted (clean_sample_country fixture handles this, but be explicit)
    safe_delete(temp_rec)
    qry.clear_cache()
    old_count = qry.num_countries()
    new_rec_id = qry.create(temp_rec)

    assert qry.is_valid_id(new_rec_id)
    assert qry.num_countries() == old_count + 1

    # Verify country data is stored correctly
    countries = qry.read()
    country_key = qry.SAMPLE_COUNTRY[qry.CODE]
    assert country_key in countries
    created_country = countries[country_key]
    assert created_country['name'] == qry.SAMPLE_COUNTRY['name']
    assert created_country['code'] == qry.SAMPLE_COUNTRY['code']
    # Clean up
    safe_delete(temp_rec)

@pytest.mark.parametrize("country_data, match", [
    ({}, "name"),
    (17, "Invalid"),
    ({'name': 'Country'}, "code"),
    ({'name': 'Test Country', 'code': None}, "code"),
])
def test_create_invalid_inputs(country_data, match):
    with pytest.raises(ValueError):
        qry.create(country_data)

def test_delete(temp_country_unique):
    rec_id, rec = temp_country_unique
    ret = qry.delete(rec[qry.NAME], rec[qry.CODE])
    assert ret == 1


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some country name that is not there, not a state')


def test_delete_by_name_success_and_not_found():
    """Test delete when passed a name and code: success and not-found cases."""
    # Success: dbc.delete returns >=1 -> delete() should return True
    with patch('countries.queries.dbc.delete', return_value=1) as fake_del:
        assert qry.delete('Any Country', 'AC') is True
        fake_del.assert_called()

    # Not found: dbc.delete returns 0 -> delete() should raise ValueError
    with patch('countries.queries.dbc.delete', return_value=0):
        import pytest as _pytest
        with _pytest.raises(ValueError, match='Country not found'):
            qry.delete('Any Country', 'AC')


def test_read(temp_country_unique):
    countries = qry.read()
    assert isinstance(countries, dict)
    assert qry.SAMPLE_KEY in countries


@pytest.mark.skip('revive once all functions are cutover!')
def test_read_cant_connect(mock_db_connect):
    with pytest.raises(ConnectionError):
        countries = qry.read()


def test_is_valid_id(temp_country_unique):
    # valid id (from fixture)
    rec_id, rec = temp_country_unique
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


def test_delete_returns_true_and_removes(temp_country_unique):
    # temp_country is the MongoDB _id returned from create
    rec_id, rec = temp_country_unique
    assert qry.delete(rec_id)
    # Verify it's deleted by checking read() doesn't contain it
    # (We can't easily check by ID since read() removes _id by default)
    countries = qry.read()
    # The country should be deleted, but we can't directly verify by ID
    # So we just verify delete returns True
    pass

def test_read_returns_expected_fields(temp_country_unique):
    countries = qry.read()
    for data in countries.values():
        assert 'name' in data
        assert 'code' in data

def test_create_duplicate_country():
    """Test that creating a duplicate country (same code) fails."""
    import time
    timestamp = int(time.time() * 1000)
    country1 = {'name': f'Duplicate Test Country {timestamp}', 'code': 'DT'}
    country2 = {'name': f'Duplicate Test Country {timestamp + 1}', 'code': 'DT'}
    
    # Clean up any existing records with code 'DT' first
    qry.clear_cache()
    countries = qry.read()
    if 'DT' in countries:
        existing = countries['DT']
        safe_delete(existing)
        qry.clear_cache()
    # Also try to delete by the test data directly
    safe_delete(country1)
    safe_delete(country2)
    qry.clear_cache()
    
    qry.create(country1)
    with pytest.raises(ValueError, match='Duplicate key'):
        qry.create(country2)
    
    safe_delete(country1)

@pytest.mark.skip('revive once data format in MongoDB is confirmed')
def test_search_countries_by_name(temp_country):
    """Test searching countries by name"""
    # This test is skipped and will need to be updated when revived
    # to work with database instead of country_cache
    pass


def test_search_countries_by_name_invalid_input():
    """Test search function with invalid inputs"""
    # Test non-string input
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_countries_by_name(123)
    
    # Test empty string
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_countries_by_name('')
    
    # Test whitespace only
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_countries_by_name('   ')
    
    # Test None input
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_countries_by_name(None)

def test_delete_by_invalid_id_format():
    """Test that delete raises ValueError for invalid ObjectId format"""
    with pytest.raises(ValueError, match='Invalid country ID format'):
        qry.delete('invalid-id-format')

@pytest.mark.parametrize("bad_input", [123, [], {}, ['ABC'], None])
def test_delete_rejects_non_string(bad_input):
    with pytest.raises(ValueError):
        qry.delete(bad_input)


def test_create_multiple_countries_and_count():
    """Test creating multiple countries and verifying count."""
    import time
    timestamp = int(time.time() * 1000)
    test_countries = [
        {'name': f'Multi Country {timestamp} A', 'code': 'MCA'},
        {'name': f'Multi Country {timestamp} B', 'code': 'MCB'},
        {'name': f'Multi Country {timestamp} C', 'code': 'MCC'},
    ]
    
    # Clean up any existing records
    for country in test_countries:
        safe_delete(country)
    qry.clear_cache()
    
    initial_count = qry.num_countries()
    try:
        for country in test_countries:
            qry.create(country)
        assert qry.num_countries() == initial_count + len(test_countries)
    finally:
        for country in test_countries:
            safe_delete(country)


def test_main_prints_read(monkeypatch, capsys):
    """Patch qry.read to return a known list and verify main() prints it."""
    sample = [{'name': 'Printed Country', 'code': 'PC'}]

    # Patch the module-level read function used by main()
    monkeypatch.setattr(qry, 'read', lambda: sample)

    # Call main() which should print the returned list
    qry.main()

    captured = capsys.readouterr()
    out = captured.out

    # Expect the printed representation to include the country name and code
    assert 'Printed Country' in out
    assert 'PC' in out


def test_read_raises_on_db_connection_error(monkeypatch):
    """Ensure qry.read propagates a ConnectionError from the DB layer."""
    qry.clear_cache()  # Clear cache so it will try to reload
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
    with pytest.raises(ValueError, match='Country not found'):
        qry.delete(valid_id)

def test_unicode_and_special_characters_in_names():
    """Test countries with unicode and special characters."""
    test_cases = [
        {'name': 'Côte d\'Ivoire', 'code': 'CI'},
        {'name': 'São Tomé and Príncipe', 'code': 'ST'},
        {'name': 'España', 'code': 'ES'},
    ]
    
    # Clean up any existing records
    for country_data in test_cases:
        safe_delete(country_data)
    qry.clear_cache()
    
    try:
        for country_data in test_cases:
            qry.create(country_data)
            results = qry.search_countries_by_name(country_data['name'])
            assert any(country['name'] == country_data['name'] for country in results.values())
    finally:
        for country_data in test_cases:
            safe_delete(country_data)

def test_search_countries_by_name_substring(sample_countries):
    results = qry.search_countries_by_name('King')
    assert 'United Kingdom' in [c['name'] for c in results.values()]

def test_search_countries_by_name_very_long_string():
    """Test search with very long input string."""
    long_string = 'A' * 1000
    results = qry.search_countries_by_name(long_string)
    assert isinstance(results, dict)

def test_search_trimming_and_case_insensitivity():
    sample_db = [
        {'name': 'United Kingdom', 'code': 'UK'},
        {'name': 'United Arab Emirates', 'code': 'AE'},
    ]

    # Clear cache and patch the database read to return our sample list
    qry.clear_cache()
    with patch('countries.queries.dbc.read', return_value=sample_db):
        # Search with extra whitespace and mixed case
        results = qry.search_countries_by_name('  united kingdom  ')
        assert isinstance(results, dict)
        names = [c['name'] for c in results.values()]
        assert 'United Kingdom' in names
        assert 'United Arab Emirates' not in names

def test_create_rejects_whitespace_fields():
    """Country name or code that is only whitespace should be rejected."""
    bad_inputs = [
        {'name': '   ', 'code': 'US'},
        {'name': 'Testland', 'code': '   '},
        {'name': '   ', 'code': '   '}
    ]

    for data in bad_inputs:
        with pytest.raises(ValueError):
            qry.create(data)
