from copy import deepcopy
from unittest.mock import patch
import pytest
import users.queries as qry


def safe_delete(user):
    try:
        qry.delete(user[qry.USERNAME])
    except ValueError:
        pass


def get_temp_rec():
    return deepcopy(qry.SAMPLE_USER)


@pytest.fixture(scope='function')
def temp_user_no_del():
    temp_rec = get_temp_rec()
    # Clean up any existing record first
    safe_delete(temp_rec)
    qry.create(get_temp_rec())
    return temp_rec


@pytest.fixture
def temp_user_unique():
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    qry.clear_cache()
    rec_id = qry.create(temp_rec)
    yield rec_id, temp_rec
    safe_delete(temp_rec)


@pytest.fixture(scope='function')
def sample_users():
    """Provide a small set of users in the database for search tests.

    This fixture creates test users in the database and cleans them up afterwards.
    """
    users_to_create = [
        {'username': 'testuser1', 'name': 'Test User One', 'email': 'test1@example.edu'},
        {'username': 'testuser2', 'name': 'Test User Two', 'email': 'test2@example.edu'},
        {'username': 'anotheruser', 'name': 'Another User', 'email': 'test3@example.edu'},
    ]
    created_usernames = []
    # Clean up any existing users first
    for user in users_to_create:
        safe_delete(user)
    qry.clear_cache()
    # Now create the users
    for user in users_to_create:
        user_id = qry.create(user)
        created_usernames.append(user[qry.USERNAME])
    try:
        yield users_to_create
    finally:
        # Clean up created users
        for username in created_usernames:
            safe_delete({'username': username})


def test_search_users_by_name_with_fixture(sample_users):
    # Search by name - partial match
    results = qry.search_users_by_name('Test')
    assert isinstance(results, dict)
    # Check that we have users with 'Test' in the name
    user_names = [user.get('name', '') for user in results.values()]
    assert 'Test User One' in user_names
    assert 'Test User Two' in user_names
    assert 'Another User' not in user_names  # Doesn't have 'Test' in name

    # Search by username - should find users with 'testuser' in username
    results_username = qry.search_users_by_name('testuser')
    assert isinstance(results_username, dict)
    usernames = [user.get('username', '') for user in results_username.values()]
    assert 'testuser1' in usernames
    assert 'testuser2' in usernames
    assert 'anotheruser' not in usernames  # Doesn't have 'testuser' in username

    # Search by name - case-insensitive match
    results_ci = qry.search_users_by_name('test user')
    user_names_ci = [user.get('name', '') for user in results_ci.values()]
    assert 'Test User One' in user_names_ci
    assert 'Test User Two' in user_names_ci

    # Search by username - case-insensitive
    results_username_ci = qry.search_users_by_name('TESTUSER')
    usernames_ci = [user.get('username', '') for user in results_username_ci.values()]
    assert 'testuser1' in usernames_ci
    assert 'testuser2' in usernames_ci

    # Search that matches both name and username
    results_both = qry.search_users_by_name('another')
    assert isinstance(results_both, dict)
    # Should find 'anotheruser' by username
    usernames_both = [user.get('username', '') for user in results_both.values()]
    names_both = [user.get('name', '') for user in results_both.values()]
    assert 'anotheruser' in usernames_both or 'Another User' in names_both


def test_search_users_by_name_no_matches():
    """Verify a search with no matches returns an empty dict."""
    # Search for a user that likely doesn't exist
    results = qry.search_users_by_name('XyZ123NonexistentUser456')
    assert isinstance(results, dict)
    assert len(results) == 0


def test_search_users_by_username():
    """Test that search works when searching by username."""
    import time
    timestamp = int(time.time() * 1000)
    test_user = {
        'username': f'searchtest{timestamp}',
        'name': 'Different Name',
        'email': 'searchtest@example.edu'
    }
    
    # Clean up first
    safe_delete(test_user)
    
    try:
        qry.create(test_user)
        
        # Search by username should find the user
        results = qry.search_users_by_name('searchtest')
        assert isinstance(results, dict)
        assert len(results) > 0
        usernames = [user.get('username', '') for user in results.values()]
        assert test_user['username'] in usernames
        
        # Search by name should also find it (if it matches)
        results_name = qry.search_users_by_name('Different')
        names = [user.get('name', '') for user in results_name.values()]
        assert test_user['name'] in names
        
        # Search that doesn't match either should return empty
        results_no_match = qry.search_users_by_name('XyZ999NoMatch')
        assert len(results_no_match) == 0
    finally:
        safe_delete(test_user)

    
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_count():
    assert qry.num_users() == len(qry.cache)


def test_count():
    # Clean up any existing user first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    qry.clear_cache()
    # get the count
    old_count = qry.num_users()
    # add a record
    qry.create(get_temp_rec())
    assert qry.num_users() == old_count + 1
    safe_delete(temp_rec)


def test_good_create():
    # Clean up any existing user first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    qry.clear_cache()
    old_count = qry.num_users()
    new_rec_id = qry.create(temp_rec)

    # id returned should be valid
    assert qry.is_valid_id(new_rec_id)

    # user count should increase
    assert qry.num_users() == old_count + 1


def test_create_dup_key():
    # Clean up any existing user first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    qry.clear_cache()
    qry.create(get_temp_rec())
    with pytest.raises(ValueError):
        qry.create(get_temp_rec())
    safe_delete(temp_rec)


@pytest.mark.parametrize("user_data, match", [
    ({}, "non-empty 'username'"),
    (17, "must be a dictionary"),
    ({'name': 'User'}, "non-empty 'username'"),
    ({'username': None}, "non-empty 'username'"),
    ({'username': 'test', 'email': 'invalid@example.com'}, "Email must end in .edu"),
])
def test_create_invalid_inputs(user_data, match):
    with pytest.raises(ValueError, match=match):
        qry.create(user_data)

def test_delete_by_username(temp_user_unique):
    rec_id, rec = temp_user_unique
    ret = qry.delete(rec[qry.USERNAME])
    assert ret is True


def test_delete_by_id(temp_user_unique):
    rec_id, rec = temp_user_unique
    ret = qry.delete(rec_id)
    assert ret is True


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some username that is not there')


def test_delete_by_username_success_and_not_found():
    """Test delete when passed a username: success and not-found cases."""
    # Success: dbc.delete returns >=1 -> delete() should return True
    with patch('users.queries.dbc.delete', return_value=1) as fake_del:
        assert qry.delete('Any User') is True
        fake_del.assert_called()

    # Not found: dbc.delete returns 0 -> delete() should raise ValueError
    with patch('users.queries.dbc.delete', return_value=0):
        import pytest as _pytest
        with _pytest.raises(ValueError, match='User not found'):
            qry.delete('Any User')


def test_read(temp_user_unique):
    users = qry.read()
    assert isinstance(users, dict)
    assert qry.SAMPLE_KEY in users


def test_is_valid_id(temp_user_unique):
    # valid id (from fixture)
    rec_id, rec = temp_user_unique
    result = qry.is_valid_id(rec_id)
    assert isinstance(result, bool)
    assert result is True

def test_read_after_delete(temp_user_unique):
    rec_id, temp_rec = temp_user_unique
    qry.delete(temp_rec[qry.USERNAME])
    users = qry.read()
    key = temp_rec[qry.USERNAME]
    assert key not in users


def test_create_duplicate_user():
    # Create unique users to avoid duplicate key errors
    import time
    timestamp = int(time.time() * 1000)
    user1 = {'username': f'duptest{timestamp}', 'name': 'Test User 1', 'email': 'test1@example.edu'}
    user2 = {'username': f'duptest{timestamp + 1}', 'name': 'Test User 2', 'email': 'test2@example.edu'}
    
    # Clean up any existing records first
    safe_delete(user1)
    safe_delete(user2)
    qry.clear_cache()
    
    rec_id1 = qry.create(user1)
    rec_id2 = qry.create(user2)
    
    assert rec_id1 != rec_id2
    # Delete by username
    qry.delete(user1[qry.USERNAME])
    qry.delete(user2[qry.USERNAME])


def test_create_multiple_users_and_count():
    """Test creating multiple users and verifying count"""
    import time
    timestamp = int(time.time() * 1000)
    test_users = [
        {'username': f'multiuser{timestamp}A', 'name': 'Multi User A', 'email': 'multia@example.edu'},
        {'username': f'multiuser{timestamp}B', 'name': 'Multi User B', 'email': 'multib@example.edu'},
        {'username': f'multiuser{timestamp}C', 'name': 'Multi User C', 'email': 'multic@example.edu'},
    ]
    
    # Clean up any existing records first
    for user in test_users:
        safe_delete(user)
    qry.clear_cache()
    
    initial_count = qry.num_users()
    created_users = []
    
    try:
        for user in test_users:
            user_id = qry.create(user)
            created_users.append(user)
        
        assert qry.num_users() == initial_count + len(test_users)
    finally:
        # Clean up
        for user in created_users:
            safe_delete(user)

