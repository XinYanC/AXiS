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


@patch('server.endpoints.stateqry.count')
def test_states_count(mock_count):
    """Test the /states/count endpoint."""
    mock_count.return_value = 50
    resp = TEST_CLIENT.get(f"{ep.STATES_EPS}/{ep.COUNT}")
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert resp_json['count'] == 50
