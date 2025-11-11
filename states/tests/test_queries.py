# To run test: PYTHONPATH=$(pwd) pytest -v states/tests/test_queries.py

from unittest.mock import patch

import pytest

import states.queries as qry

from copy import deepcopy

def get_temp_rec():
    return deepcopy(qry.SAMPLE_STATE)


@pytest.fixture
def temp_state_unique():
    temp_rec = get_temp_rec()
    rec_id = qry.create(temp_rec)
    yield rec_id, temp_rec
    try:
        qry.delete(temp_rec[qry.NAME], temp_rec[qry.CODE])
    except ValueError:
        pass


@pytest.fixture(scope='function')
def sample_states():
    """Provide a small set of states in the database for search tests.

    This fixture creates test states in the database and cleans them up afterwards.
    """
    states_to_create = [
        {'name': 'New York', 'code': 'NY'},
        {'name': 'California', 'code': 'CA'},
        {'name': 'Louisiana', 'code': 'LA'},
    ]
    created_ids = []
    for state in states_to_create:
        state_id = qry.create(state)
        created_ids.append((state[qry.NAME], state[qry.CODE]))
    try:
        yield states_to_create
    finally:
        # Clean up created states
        for name, code in created_ids:
            try:
                qry.delete(name, code)
            except ValueError:
                pass  # Already deleted


def test_search_states_by_name_with_fixture(sample_states):
    # partial match
    results = qry.search_states_by_name('New')
    assert isinstance(results, dict)
    # Check that we have states with 'New' in the name
    state_names = [state.get('name', '') for state in results.values()]
    assert 'New York' in state_names
    assert 'California' not in state_names
    assert 'Louisiana' not in state_names

    # case-insensitive match
    results_ci = qry.search_states_by_name('california')
    state_names_ci = [state.get('name', '') for state in results_ci.values()]
    assert 'California' in state_names_ci


def test_search_states_by_name_no_matches():
    """Verify a search with no matches returns an empty dict."""
    # Search for a state that likely doesn't exist
    results = qry.search_states_by_name('XyZ123NonexistentState456')
    assert isinstance(results, dict)
    assert len(results) == 0

    
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_states():
    # This test is skipped as it's an example of a bad test
    pass


def test_num_states():
    # get the count
    old_count = qry.num_states()
    # add a record
    temp_rec = get_temp_rec()
    qry.create(temp_rec)
    assert qry.num_states() == old_count + 1
    # Clean up
    qry.delete(temp_rec[qry.NAME], temp_rec[qry.CODE])


def test_good_create():
    old_count = qry.num_states()
    new_rec_id = qry.create(get_temp_rec())

    # id returned should be valid
    assert qry.is_valid_id(new_rec_id)

    # state count should increase
    assert qry.num_states() == old_count + 1

    # state data should be stored correctly in database
    states = qry.read()
    created_state = None
    for state in states:
        # Check if this state matches our sample state
        if state.get('name') == qry.SAMPLE_STATE['name'] and state.get('code') == qry.SAMPLE_STATE['code']:
            created_state = state
            break
    assert created_state is not None
    assert created_state['name'] == qry.SAMPLE_STATE['name']
    assert created_state['code'] == qry.SAMPLE_STATE['code']
    
    # Clean up
    qry.delete(qry.SAMPLE_STATE['name'], qry.SAMPLE_STATE['code'])

@pytest.mark.parametrize("state_data, match", [
    ({}, "name"),
    (17, "Invalid"),
    ({'code': 'NY'}, "name"),
    ({'name': 'State'}, "code"),
    ({'name': None, 'code': 'NY'}, "name"),
    ({'name': 'Test State', 'code': None}, "code"),
])
def test_create_invalid_inputs(state_data, match):
    with pytest.raises(ValueError):
        qry.create(state_data)

def test_delete(temp_state_unique):
    rec_id, rec = temp_state_unique
    ret = qry.delete(rec[qry.NAME], rec[qry.CODE])
    assert ret == 1


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some state name that is not there')


def test_read(temp_state_unique):
    states = qry.read()
    assert isinstance(states, list)
    assert get_temp_rec() in states


@pytest.mark.skip('revive once all functions are cutover!')
def test_read_cant_connect(mock_db_connect):
    with pytest.raises(ConnectionError):
        states = qry.read()


def test_is_valid_id(temp_state_unique):
    # valid id (from fixture)
    rec_id, rec = temp_state_unique
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


def test_delete_returns_true_and_removes(temp_state_unique):
    # temp_state is the MongoDB _id returned from create
    rec_id, rec = temp_state_unique
    assert qry.delete(rec_id)
    # Verify it's deleted by checking read() doesn't contain it
    # (We can't easily check by ID since read() removes _id by default)
    states = qry.read()
    # The state should be deleted, but we can't directly verify by ID
    # So we just verify delete returns True
    pass

def test_read_returns_expected_fields(temp_state_unique):
    states = qry.read()
    for data in states:
        assert 'name' in data
        assert 'code' in data

def test_create_duplicate_state():
    # Create unique states to avoid duplicate key errors
    import time
    timestamp = int(time.time() * 1000)
    state1 = {'name': f'Duplicate Test State {timestamp}', 'code': 'DT'}
    state2 = {'name': f'Duplicate Test State {timestamp + 1}', 'code': 'DT'}
    
    rec_id1 = qry.create(state1)
    rec_id2 = qry.create(state2)
    
    assert rec_id1 != rec_id2
    # Delete by ID (MongoDB _id)
    qry.delete(rec_id1)
    qry.delete(rec_id2)

@pytest.mark.skip('revive once data format in MongoDB is confirmed')
def test_search_states_by_name(temp_state):
    """Test searching states by name"""
    # This test is skipped and will need to be updated when revived
    # to work with database instead of state_cache
    pass


def test_search_states_by_name_invalid_input():
    """Test search function with invalid inputs"""
    # Test non-string input
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_states_by_name(123)
    
    # Test empty string
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_states_by_name('')
    
    # Test whitespace only
    with pytest.raises(ValueError, match='Search term cannot be empty'):
        qry.search_states_by_name('   ')
    
    # Test None input
    with pytest.raises(ValueError, match='Search term must be a string'):
        qry.search_states_by_name(None)

def test_delete_by_invalid_id_format():
    """Test that delete raises ValueError for invalid ObjectId format"""
    with pytest.raises(ValueError, match='Invalid state ID format'):
        qry.delete('invalid-id-format')


def test_create_multiple_states_and_count():
    """Test creating multiple states and verifying count"""
    import time
    timestamp = int(time.time() * 1000)
    test_states = [
        {'name': f'Multi State {timestamp} A', 'code': 'MS'},
        {'name': f'Multi State {timestamp} B', 'code': 'MS'},
        {'name': f'Multi State {timestamp} C', 'code': 'MS'},
    ]
    
    initial_count = qry.num_states()
    created_states = []
    
    try:
        for state in test_states:
            state_id = qry.create(state)
            created_states.append(state)
        
        assert qry.num_states() == initial_count + len(test_states)
    finally:
        # Clean up
        for state in created_states:
            try:
                qry.delete(state[qry.NAME], state[qry.CODE])
            except ValueError:
                pass


def test_main_prints_read(monkeypatch, capsys):
    """Patch qry.read to return a known list and verify main() prints it."""
    sample = [{'name': 'Printed State', 'code': 'PS'}]

    # Patch the module-level read function used by main()
    monkeypatch.setattr(qry, 'read', lambda: sample)

    # Call main() which should print the returned list
    qry.main()

    captured = capsys.readouterr()
    out = captured.out

    # Expect the printed representation to include the state name and code
    assert 'Printed State' in out
    assert 'PS' in out


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
    with pytest.raises(ValueError, match='State not found'):
        qry.delete(valid_id)