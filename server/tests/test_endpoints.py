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
