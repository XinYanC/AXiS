from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


# ==================== CITIES ENDPOINT TESTS ====================

@patch('server.endpoints.cityqry.read')
def test_cities_read(mock_read):
    """Test the /cities/read endpoint returns the mocked cities and count."""
    # Arrange: mock the read() call to return a predictable list
    mock_data = [
        {"name": "Alpha", "population": 100},
        {"name": "Beta", "population": 200},
    ]
    mock_read.return_value = mock_data

    # Act
    resp = TEST_CLIENT.get(f"{ep.CITIES_EPS}/{ep.READ}")
    resp_json = resp.get_json()

    # Assert
    assert ep.CITY_RESP in resp_json
    assert resp_json[ep.CITY_RESP] == mock_data
    assert resp_json[ep.NUM_RECS] == len(mock_data)


@patch('server.endpoints.cityqry.search_cities_by_name')
def test_cities_search(mock_search):
    """Test the /cities/search endpoint."""
    # Arrange
    mock_results = {
        "id1": {"name": "New York", "state_code": "NY"},
        "id2": {"name": "York", "state_code": "PA"},
    }
    mock_search.return_value = mock_results

    # Act
    resp = TEST_CLIENT.get(f"{ep.CITIES_EPS}/{ep.SEARCH}?q=york")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.CITY_RESP in resp_json
    assert resp_json[ep.CITY_RESP] == mock_results
    assert resp_json[ep.NUM_RECS] == len(mock_results)
    assert resp_json['search_term'] == 'york'


def test_cities_search_missing_query():
    """Test the /cities/search endpoint without query parameter."""
    resp = TEST_CLIENT.get(f"{ep.CITIES_EPS}/{ep.SEARCH}")
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


@patch('server.endpoints.cityqry.num_cities')
def test_cities_count(mock_count):
    """Test the /cities/count endpoint."""
    # Arrange
    mock_count.return_value = 42

    # Act
    resp = TEST_CLIENT.get(f"{ep.CITIES_EPS}/{ep.COUNT}")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert resp_json['count'] == 42

@patch('server.endpoints.cityqry.create')
def test_cities_create(mock_create):
    """Test the /cities/create endpoint."""
    # Arrange
    mock_create.return_value = '507f1f77bcf86cd799439011'
    city_data = {"name": "Test City", "state_code": "CA"}

    # Act
    resp = TEST_CLIENT.post(
        f"{ep.CITIES_EPS}/{ep.CREATE}",
        json=city_data,
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == 201
    assert ep.MESSAGE in resp_json
    assert resp_json['id'] == '507f1f77bcf86cd799439011'
    assert resp_json['city'] == city_data
    mock_create.assert_called_once()


@patch('server.endpoints.cityqry.create')
def test_cities_create_invalid_data(mock_create):
    """Test the /cities/create endpoint with invalid data."""
    # Arrange
    mock_create.side_effect = ValueError('City must have a non-empty name.')

    # Act
    resp = TEST_CLIENT.post(
        f"{ep.CITIES_EPS}/{ep.CREATE}",
        json={"name": "", "state_code": "CA"},
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == 400
    assert ep.ERROR in resp_json

@patch('server.endpoints.cityqry.delete')
def test_cities_delete(mock_delete):
    """Test the /cities/delete endpoint."""
    # Arrange
    mock_delete.return_value = True

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.CITIES_EPS}/{ep.DELETE}?name=Test%20City&state_code=CA"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.MESSAGE in resp_json
    mock_delete.assert_called_once_with("Test City", "CA")


@patch('server.endpoints.cityqry.delete')
def test_cities_delete_not_found(mock_delete):
    """Test the /cities/delete endpoint when city not found."""
    # Arrange
    mock_delete.side_effect = ValueError('City not found: Test, CA')

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.CITIES_EPS}/{ep.DELETE}?name=Test&state_code=CA"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == NOT_FOUND
    assert ep.ERROR in resp_json


def test_cities_delete_missing_params():
    """Test the /cities/delete endpoint without required params."""
    resp = TEST_CLIENT.delete(f"{ep.CITIES_EPS}/{ep.DELETE}?name=Test")
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


# ==================== COUNTRIES ENDPOINT TESTS ====================

@patch('server.endpoints.countryqry.read')
def test_countries_read(mock_read):
    """Test the /countries/read endpoint returns the mocked countries and count."""
    # Arrange: mock the read() call to return a predictable dict
    mock_data = {
        "USA": {"name": "United States", "code": "USA"},
        "FRA": {"name": "France", "code": "FRA"},
        "GBR": {"name": "United Kingdom", "code": "GBR"},
    }
    mock_read.return_value = mock_data

    # Act
    resp = TEST_CLIENT.get(f"{ep.COUNTRIES_EPS}/{ep.READ}")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.COUNTRY_RESP in resp_json
    assert resp_json[ep.COUNTRY_RESP] == mock_data
    assert resp_json[ep.NUM_RECS] == len(mock_data)


@patch('server.endpoints.countryqry.search_countries_by_name')
def test_countries_search(mock_search):
    """Test the /countries/search endpoint."""
    # Arrange
    mock_results = {
        "id1": {"name": "United States", "code": "US"},
        "id2": {"name": "United Kingdom", "code": "UK"},
    }
    mock_search.return_value = mock_results

    # Act
    resp = TEST_CLIENT.get(f"{ep.COUNTRIES_EPS}/{ep.SEARCH}?q=united")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.COUNTRY_RESP in resp_json
    assert resp_json[ep.NUM_RECS] == len(mock_results)


@patch('server.endpoints.countryqry.num_countries')
def test_countries_count(mock_count):
    """Test the /countries/count endpoint."""
    mock_count.return_value = 10
    resp = TEST_CLIENT.get(f"{ep.COUNTRIES_EPS}/{ep.COUNT}")
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert resp_json['count'] == 10

@patch('server.endpoints.countryqry.create')
def test_countries_create(mock_create):
    """Test the /countries/create endpoint."""
    # Arrange
    mock_create.return_value = '507f1f77bcf86cd799439012'
    country_data = {"name": "Test Country", "code": "TC"}

    # Act
    resp = TEST_CLIENT.post(
        f"{ep.COUNTRIES_EPS}/{ep.CREATE}",
        json=country_data,
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == 201
    assert ep.MESSAGE in resp_json
    assert resp_json['id'] == '507f1f77bcf86cd799439012'
    assert resp_json['country'] == country_data

@patch('server.endpoints.countryqry.delete')
def test_countries_delete(mock_delete):
    """Test the /countries/delete endpoint."""
    # Arrange
    mock_delete.return_value = True

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.COUNTRIES_EPS}/{ep.DELETE}?name=Test%20Country&code=TC"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.MESSAGE in resp_json
    mock_delete.assert_called_once_with("Test Country", "TC")


# ==================== STATES ENDPOINT TESTS ====================

@patch('server.endpoints.stateqry.read')
def test_states_read(mock_read):
    """Test the /states/read endpoint returns the mocked states and count."""
    # Arrange: mock the read() call to return a predictable dict
    mock_data = {
        "NY,USA": {"name": "New York", "code": "NY", "country_code": "USA"},
        "CA,USA": {"name": "California", "code": "CA", "country_code": "USA"},
        "TX,USA": {"name": "Texas", "code": "TX", "country_code": "USA"},
    }
    mock_read.return_value = mock_data

    # Act
    resp = TEST_CLIENT.get(f"{ep.STATES_EPS}/{ep.READ}")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.STATE_RESP in resp_json
    assert resp_json[ep.STATE_RESP] == mock_data
    assert resp_json[ep.NUM_RECS] == len(mock_data)


@patch('server.endpoints.stateqry.search_states_by_name')
def test_states_search(mock_search):
    """Test the /states/search endpoint."""
    # Arrange
    mock_results = {
        "NY,USA": {"name": "New York", "code": "NY", "country_code": "USA"},
        "NYC,USA": {"name": "New York City", "code": "NYC", "country_code": "USA"},
    }
    mock_search.return_value = mock_results

    # Act
    resp = TEST_CLIENT.get(f"{ep.STATES_EPS}/{ep.SEARCH}?q=york")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.STATE_RESP in resp_json
    assert resp_json[ep.NUM_RECS] == len(mock_results)
    assert resp_json['search_term'] == 'york'


@patch('server.endpoints.stateqry.num_states')
def test_states_count(mock_count):
    """Test the /states/count endpoint."""
    mock_count.return_value = 50
    resp = TEST_CLIENT.get(f"{ep.STATES_EPS}/{ep.COUNT}")
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert resp_json['count'] == 50

@patch('server.endpoints.stateqry.create')
def test_states_create(mock_create):
    """Test the /states/create endpoint."""
    # Arrange
    mock_create.return_value = '507f1f77bcf86cd799439013'
    state_data = {
        "name": "Test State",
        "code": "TS",
        "country_code": "USA",
    }

    # Act
    resp = TEST_CLIENT.post(
        f"{ep.STATES_EPS}/{ep.CREATE}",
        json=state_data,
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == 201
    assert ep.MESSAGE in resp_json
    assert resp_json['id'] == '507f1f77bcf86cd799439013'
    assert resp_json['state'] == state_data

@patch('server.endpoints.stateqry.delete')
def test_states_delete(mock_delete):
    """Test the /states/delete endpoint."""
    # Arrange
    mock_delete.return_value = True

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.STATES_EPS}/{ep.DELETE}?code=TS&country_code=USA"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.MESSAGE in resp_json
    mock_delete.assert_called_once_with("TS", "USA")


def test_states_delete_missing_params():
    """Test the /states/delete endpoint without required params."""
    resp = TEST_CLIENT.delete(
        f"{ep.STATES_EPS}/{ep.DELETE}?code=TS"
    )
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json
