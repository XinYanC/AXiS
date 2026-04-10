from http.client import (
    BAD_REQUEST,
    NOT_FOUND,
    OK,
    UNAUTHORIZED,
)
from io import BytesIO

from unittest.mock import patch

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    assert resp.status_code == OK
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
    city_data = {
        "name": "Test City",
        "state_code": "CA",
        "latitude": 34.05,
        "longitude": -118.24,
    }

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

# ==================== USERS ENDPOINT TESTS ====================

@patch('server.endpoints.userqry.read')
def test_users_read(mock_read):
    """Test the /users/read endpoint returns the mocked users and count."""
    # Arrange: mock the read() call to return a predictable dict
    mock_data = {
        "user1": {"username": "johndoe", "name": "John Doe", "email": "john@example.edu"},
        "user2": {"username": "janedoe", "name": "Jane Doe", "email": "jane@example.edu"},
        "user3": {"username": "bobsmith", "name": "Bob Smith", "email": "bob@example.edu"},
    }
    mock_read.return_value = mock_data

    # Act
    resp = TEST_CLIENT.get(f"{ep.USERS_EPS}/{ep.READ}")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.USER_RESP in resp_json
    assert resp_json[ep.USER_RESP] == mock_data
    assert resp_json[ep.NUM_RECS] == len(mock_data)


@patch('server.endpoints.userqry.search_users_by_name')
def test_users_search(mock_search):
    """Test the /users/search endpoint."""
    # Arrange
    mock_results = {
        "user1": {"username": "johndoe", "name": "John Doe", "email": "john@example.edu"},
        "user2": {"username": "janedoe", "name": "Jane Doe", "email": "jane@example.edu"},
    }
    mock_search.return_value = mock_results

    # Act
    resp = TEST_CLIENT.get(f"{ep.USERS_EPS}/{ep.SEARCH}?q=doe")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.USER_RESP in resp_json
    assert resp_json[ep.USER_RESP] == mock_results
    assert resp_json[ep.NUM_RECS] == len(mock_results)
    assert resp_json['search_term'] == 'doe'


@patch('server.endpoints.userqry.num_users')
def test_users_count(mock_count):
    """Test the /users/count endpoint."""
    # Arrange
    mock_count.return_value = 42

    # Act
    resp = TEST_CLIENT.get(f"{ep.USERS_EPS}/{ep.COUNT}")
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert resp_json['count'] == 42
    assert ep.USER_RESP in resp_json


@patch('server.endpoints.userqry.create')
def test_users_create(mock_create):
    """Test the /users/create endpoint."""
    # Arrange
    mock_create.return_value = '507f1f77bcf86cd799439014'
    user_data = {
        "username": "testuser",
        "password": "password123",
        "name": "Test User",
        "email": "testuser@example.edu",
        "age": 25,
        "bio": "Test bio",
        "is_verified": False,
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "rating": 4.5,
    }

    # Act
    resp = TEST_CLIENT.post(
        f"{ep.USERS_EPS}/{ep.CREATE}",
        json=user_data,
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == 201
    assert ep.MESSAGE in resp_json
    assert resp_json['id'] == '507f1f77bcf86cd799439014'
    assert resp_json['user']['username'] == user_data['username']
    # Password should be redacted in the response body.
    assert resp_json['user']['password'] == '[REDACTED]'
    # created_at is server-generated and should not be required in input.
    called_payload = mock_create.call_args.args[0]
    assert 'created_at' not in called_payload
    mock_create.assert_called_once()


def test_user_model_created_at_is_readonly():
    """Swagger model marks created_at as a server-generated read-only field."""
    assert 'created_at' in ep.user_model
    created_at_field = ep.user_model['created_at']
    assert getattr(created_at_field, 'readonly', False) is True
    schema = getattr(created_at_field, '__schema__', {})
    assert schema.get('readOnly') is True


def test_user_model_includes_rating():
    """Swagger model exposes rating as an optional float field."""
    assert 'rating' in ep.user_model


@patch('server.endpoints.userqry.update')
def test_users_update_success(mock_update):
    """Test PUT /users/update with valid username and body."""
    mock_updated = {
        'username': 'testuser',
        'name': 'Updated Name'
    }
    mock_update.return_value = mock_updated
    body = {'name': 'Updated Name'}

    resp = TEST_CLIENT.put(
        f"{ep.USERS_EPS}/{ep.UPDATE}?username=testuser",
        json=body,
    )
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.USER_RESP in resp_json
    assert resp_json[ep.USER_RESP]['name'] == 'Updated Name'
    assert ep.MESSAGE in resp_json
    mock_update.assert_called_once_with('testuser', body)


def test_users_update_missing_username():
    """Test PUT /users/update without username param returns 400."""
    resp = TEST_CLIENT.put(
        f"{ep.USERS_EPS}/{ep.UPDATE}",
        json={'name': 'X'},
    )
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


@patch('server.endpoints.userqry.delete')
def test_users_delete_by_username(mock_delete):
    """Test the /users/delete endpoint."""
    # Arrange
    mock_delete.return_value = True

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.USERS_EPS}/{ep.DELETE}?username=testuser"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.MESSAGE in resp_json
    mock_delete.assert_called_once_with("testuser")


@patch('server.endpoints.userqry.delete')
def test_users_delete_by_id(mock_delete):
    """Test the /users/delete endpoint with ObjectId."""
    # Arrange
    mock_delete.return_value = True
    object_id = '507f1f77bcf86cd799439014'

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.USERS_EPS}/{ep.DELETE}?username={object_id}"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == OK
    assert ep.MESSAGE in resp_json
    mock_delete.assert_called_once_with(object_id)


@patch('server.endpoints.userqry.delete')
def test_users_delete_not_found(mock_delete):
    """Test the /users/delete endpoint when user not found."""
    # Arrange
    mock_delete.side_effect = ValueError('User not found: testuser')

    # Act
    resp = TEST_CLIENT.delete(
        f"{ep.USERS_EPS}/{ep.DELETE}?username=testuser"
    )
    resp_json = resp.get_json()

    # Assert
    assert resp.status_code == NOT_FOUND
    assert ep.ERROR in resp_json


# ==================== LISTINGS ENDPOINT TESTS ====================

@patch('server.endpoints.listingqry.read')
def test_listings_read(mock_read):
    """Test the /listings/read endpoint."""
    mock_data = {
        'id1': {'title': 'Item A', 'description': 'Desc A', 'owner': 'a@nyu.edu'},
        'id2': {'title': 'Item B', 'description': 'Desc B', 'owner': 'b@nyu.edu'},
    }
    mock_read.return_value = mock_data

    resp = TEST_CLIENT.get(f"{ep.LISTINGS_EPS}/{ep.READ}")
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.LISTING_RESP in resp_json
    assert resp_json[ep.LISTING_RESP] == mock_data
    assert resp_json[ep.NUM_RECS] == len(mock_data)


@patch('server.endpoints.listingqry.num_listings')
def test_listings_count(mock_count):
    """Test GET /listings/count endpoint."""
    mock_count.return_value = 15

    resp = TEST_CLIENT.get(f"{ep.LISTINGS_EPS}/{ep.COUNT}")
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert resp_json['count'] == 15
    assert ep.LISTING_RESP in resp_json


@patch('server.endpoints.listingqry.search_listings_by_title')
def test_listings_search(mock_search):
    """Test GET /listings/search endpoint."""
    mock_results = {
        'id1': {'title': 'Calculus Textbook', 'description': 'Desc', 'owner': 'a@nyu.edu'},
        'id2': {'title': 'Physics Textbook', 'description': 'Desc', 'owner': 'b@nyu.edu'},
    }
    mock_search.return_value = mock_results

    resp = TEST_CLIENT.get(f"{ep.LISTINGS_EPS}/{ep.SEARCH}?q=textbook")
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.LISTING_RESP in resp_json
    assert resp_json[ep.LISTING_RESP] == mock_results
    assert resp_json[ep.NUM_RECS] == len(mock_results)
    assert resp_json['search_term'] == 'textbook'
    mock_search.assert_called_once_with('textbook')


@patch('server.endpoints.listingqry.search_listings_by_owner')
def test_listings_by_user(mock_search_by_owner):
    """Test GET /listings/by-user endpoint."""
    mock_results = {
        'id1': {'title': 'Calculus Textbook', 'owner': 'testuser'},
        'id2': {'title': 'Desk Lamp', 'owner': 'testuser'},
    }
    mock_search_by_owner.return_value = mock_results

    resp = TEST_CLIENT.get(
        f"{ep.LISTINGS_EPS}/{ep.BY_USER}?username=testuser"
    )
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.LISTING_RESP in resp_json
    assert resp_json[ep.LISTING_RESP] == mock_results
    assert resp_json[ep.NUM_RECS] == len(mock_results)
    assert resp_json['username'] == 'testuser'
    mock_search_by_owner.assert_called_once_with('testuser')


def test_listings_by_user_missing_username():
    """Test GET /listings/by-user without username returns 400."""
    resp = TEST_CLIENT.get(f"{ep.LISTINGS_EPS}/{ep.BY_USER}")
    resp_json = resp.get_json()

    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


@patch('server.endpoints.cloudinarycon.upload_image')
def test_listings_upload_image_success(mock_upload):
    """Test POST /listings/upload-image with a valid multipart file."""
    expected_url = 'https://res.cloudinary.com/demo/image/upload/test.png'
    mock_upload.return_value = expected_url

    resp = TEST_CLIENT.post(
        f"{ep.LISTINGS_EPS}/{ep.UPLOAD_IMAGE}",
        data={'image': (BytesIO(b'fake-image-bytes'), 'test.png')},
        content_type='multipart/form-data',
    )
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert resp_json['url'] == expected_url
    called_file = mock_upload.call_args.args[0]
    assert called_file.filename == 'test.png'


def test_listings_upload_image_missing_file():
    """Test POST /listings/upload-image without image field returns 400."""
    resp = TEST_CLIENT.post(
        f"{ep.LISTINGS_EPS}/{ep.UPLOAD_IMAGE}",
        data={},
        content_type='multipart/form-data',
    )
    resp_json = resp.get_json()

    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


def test_listings_upload_image_empty_filename():
    """Test POST /listings/upload-image with empty filename returns 400."""
    resp = TEST_CLIENT.post(
        f"{ep.LISTINGS_EPS}/{ep.UPLOAD_IMAGE}",
        data={'image': (BytesIO(b'abc'), '')},
        content_type='multipart/form-data',
    )
    resp_json = resp.get_json()

    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


@patch('server.endpoints.cloudinarycon.upload_image')
def test_listings_upload_image_cloudinary_error(mock_upload):
    """Test POST /listings/upload-image when Cloudinary helper fails."""
    mock_upload.side_effect = ValueError('CLOUDINARY_API_KEY not set')

    resp = TEST_CLIENT.post(
        f"{ep.LISTINGS_EPS}/{ep.UPLOAD_IMAGE}",
        data={'image': (BytesIO(b'fake-image-bytes'), 'test.png')},
        content_type='multipart/form-data',
    )
    resp_json = resp.get_json()

    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


@patch('server.endpoints.listingqry.create')
def test_listings_create(mock_create):
    """Test POST /listings/create endpoint."""
    mock_create.return_value = '507f1f77bcf86cd799439011'
    listing_data = {
        'title': 'Desk Lamp',
        'description': 'LED lamp, good condition',
        'transaction_type': 'sell',
        'owner': 'student@nyu.edu',
        'city': 'New York',
        'state': 'NY',
        'country': 'USA',
    }

    resp = TEST_CLIENT.post(
        f"{ep.LISTINGS_EPS}/{ep.CREATE}",
        json=listing_data,
    )
    resp_json = resp.get_json()

    assert resp.status_code == 201
    assert ep.MESSAGE in resp_json
    assert resp_json['id'] == '507f1f77bcf86cd799439011'
    assert resp_json['listing']['title'] == listing_data['title']
    mock_create.assert_called_once()


@patch('server.endpoints.listingqry.update')
def test_listings_update_success(mock_update):
    """Test PUT /listings/update with valid id and body."""
    listing_id = '507f1f77bcf86cd799439011'
    mock_updated = {
        '_id': listing_id,
        'title': 'Updated Title'
    }
    mock_update.return_value = mock_updated
    body = {'title': 'Updated Title'}

    resp = TEST_CLIENT.put(
        f"{ep.LISTINGS_EPS}/{ep.UPDATE}?id={listing_id}",
        json=body,
    )
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.LISTING_RESP in resp_json
    assert resp_json[ep.LISTING_RESP]['title'] == 'Updated Title'
    assert ep.MESSAGE in resp_json
    mock_update.assert_called_once_with(listing_id, body)


def test_listings_update_missing_id():
    """Test PUT /listings/update without id param returns 400."""
    resp = TEST_CLIENT.put(
        f"{ep.LISTINGS_EPS}/{ep.UPDATE}",
        json={'title': 'X'},
    )
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


@patch('server.endpoints.listingqry.delete')
def test_listings_delete_success(mock_delete):
    """Test DELETE /listings/delete with valid id."""
    mock_delete.return_value = True
    listing_id = '507f1f77bcf86cd799439011'

    resp = TEST_CLIENT.delete(
        f"{ep.LISTINGS_EPS}/{ep.DELETE}?id={listing_id}"
    )
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.MESSAGE in resp_json
    assert listing_id in resp_json[ep.MESSAGE]
    mock_delete.assert_called_once_with(listing_id)


def test_listings_delete_missing_id():
    """Test DELETE /listings/delete without id param returns 400."""
    resp = TEST_CLIENT.delete(f"{ep.LISTINGS_EPS}/{ep.DELETE}")
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json


# ==================== AUTH ENDPOINT TESTS ====================

@patch('server.endpoints.userqry.authenticate')
def test_auth_login_success(mock_authenticate):
    """Test POST /auth/login with valid email and password."""
    mock_user = {
        'username': 'johndoe',
        'name': 'John Doe',
        'email': 'johndoe@example.edu',
    }
    mock_authenticate.return_value = mock_user

    resp = TEST_CLIENT.post(
        ep.AUTH_LOGIN_EP,
        json={'email': 'johndoe@example.edu', 'password': 'secret123'},
    )
    resp_json = resp.get_json()

    assert resp.status_code == OK
    assert ep.USER_RESP in resp_json
    assert resp_json[ep.USER_RESP] == mock_user
    assert ep.MESSAGE in resp_json
    assert 'password' not in resp_json[ep.USER_RESP]
    mock_authenticate.assert_called_once_with(
        'johndoe@example.edu', 'secret123'
    )


@patch('server.endpoints.userqry.authenticate')
def test_auth_login_invalid_credentials(mock_authenticate):
    """Test POST /auth/login with wrong email or password."""
    mock_authenticate.return_value = None

    resp = TEST_CLIENT.post(
        ep.AUTH_LOGIN_EP,
        json={'email': 'wrong@example.edu', 'password': 'wrong'},
    )
    resp_json = resp.get_json()

    assert resp.status_code == UNAUTHORIZED
    assert ep.ERROR in resp_json
    assert 'Invalid email or password' in resp_json[ep.ERROR]


def test_auth_login_missing_email():
    """Test POST /auth/login without email returns 400."""
    resp = TEST_CLIENT.post(
        ep.AUTH_LOGIN_EP,
        json={'password': 'secret123'},
    )
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json
    assert 'Email' in resp_json[ep.ERROR]


def test_auth_login_missing_password():
    """Test POST /auth/login without password returns 400."""
    resp = TEST_CLIENT.post(
        ep.AUTH_LOGIN_EP,
        json={'email': 'johndoe@example.edu'},
    )
    resp_json = resp.get_json()
    assert resp.status_code == BAD_REQUEST
    assert ep.ERROR in resp_json
    assert 'Password' in resp_json[ep.ERROR]


# ==================== SYSTEM DROPDOWN ENDPOINT TESTS ====================


def test_system_dropdown_form_get():
    """GET /system/dropdown-form returns form metadata and HATEOAS _links."""
    resp = TEST_CLIENT.get(f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_FORM}')
    assert resp.status_code == OK
    data = resp.get_json()
    assert 'form' in data
    assert isinstance(data['form'], list)
    assert len(data['form']) >= 1
    assert 'form_descr' in data
    assert 'fld_names' in data
    assert isinstance(data['fld_names'], list)
    assert 'country' in data['fld_names']
    assert 'transaction_type' in data['fld_names']
    assert '_links' in data
    assert data['_links']['self']['href'].endswith(
        f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_FORM}'
    )
    assert 'options' in data['_links']


@patch('server.endpoints.countryqry.read')
def test_system_dropdown_options_countries(mock_read):
    """GET /system/dropdown-options without query returns countries as options."""
    mock_read.return_value = {
        'USA': {'name': 'United States', 'code': 'USA'},
        'CAN': {'name': 'Canada', 'code': 'CAN'},
    }
    resp = TEST_CLIENT.get(f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_OPTIONS}')
    assert resp.status_code == OK
    data = resp.get_json()
    assert data['kind'] == 'countries'
    assert data[ep.NUM_RECS] == 2
    values = {o['value'] for o in data['options']}
    assert values == {'USA', 'CAN'}
    assert all('value' in o and 'label' in o for o in data['options'])
    assert '_links' in data
    assert 'form' in data['_links']


@patch('server.endpoints.stateqry.read')
def test_system_dropdown_options_states(mock_read):
    """GET /system/dropdown-options?country_code= filters states (case-insensitive)."""
    mock_read.return_value = {
        'NY,USA': {'name': 'New York', 'code': 'NY', 'country_code': 'USA'},
        'TX,USA': {'name': 'Texas', 'code': 'TX', 'country_code': 'USA'},
        'ON,CAN': {'name': 'Ontario', 'code': 'ON', 'country_code': 'CAN'},
    }
    resp = TEST_CLIENT.get(
        f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_OPTIONS}?country_code=usa'
    )
    assert resp.status_code == OK
    data = resp.get_json()
    assert data['kind'] == 'states'
    assert data['country_code'] == 'usa'
    assert data[ep.NUM_RECS] == 2
    codes = {o['value'] for o in data['options']}
    assert codes == {'NY', 'TX'}


@patch('server.endpoints.cityqry.read')
def test_system_dropdown_options_cities(mock_read):
    """GET /system/dropdown-options?state_code= returns USA cities by default."""
    mock_read.return_value = {
        'a': {'name': 'Buffalo', 'state_code': 'NY', 'country_code': 'USA'},
        'b': {'name': 'Albany', 'state_code': 'NY', 'country_code': 'USA'},
        'c': {'name': 'Houston', 'state_code': 'TX', 'country_code': 'USA'},
        'd': {'name': 'Toronto', 'state_code': 'ON', 'country_code': 'CAN'},
    }
    resp = TEST_CLIENT.get(
        f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_OPTIONS}?state_code=ny'
    )
    assert resp.status_code == OK
    data = resp.get_json()
    assert data['kind'] == 'cities'
    assert data['state_code'] == 'ny'
    assert data['country_code'] == 'USA'
    assert data[ep.NUM_RECS] == 2
    city_names = {o['value'] for o in data['options']}
    assert city_names == {'Buffalo', 'Albany'}


@patch('server.endpoints.cityqry.read')
def test_system_dropdown_options_cities_with_country(mock_read):
    """Cities list respects country_code (e.g. ON + CAN vs WA + USA)."""
    mock_read.return_value = {
        'a': {'name': 'Seattle', 'state_code': 'WA', 'country_code': 'USA'},
        'b': {'name': 'Perth', 'state_code': 'WA', 'country_code': 'AUS'},
    }
    resp_usa = TEST_CLIENT.get(
        f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_OPTIONS}'
        f'?state_code=wa&country_code=USA'
    )
    assert resp_usa.status_code == OK
    d_usa = resp_usa.get_json()
    assert {o['value'] for o in d_usa['options']} == {'Seattle'}

    resp_aus = TEST_CLIENT.get(
        f'{ep.SYSTEM_EPS}/{ep.SYSTEM_DROPDOWN_OPTIONS}'
        f'?state_code=wa&country_code=AUS'
    )
    assert resp_aus.status_code == OK
    d_aus = resp_aus.get_json()
    assert {o['value'] for o in d_aus['options']} == {'Perth'}
