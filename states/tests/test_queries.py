from copy import deepcopy

from unittest.mock import patch
import pytest

import states.queries as qry


def safe_delete(state):
    try:
        qry.delete(state[qry.CODE], state[qry.COUNTRY_CODE])
    except ValueError:
        pass


def get_temp_rec():
    return deepcopy(qry.SAMPLE_STATE)


@pytest.fixture(scope='function')
def temp_state_no_del():
    temp_rec = get_temp_rec()
    # Clean up any existing record first
    safe_delete(temp_rec)
    qry.create(get_temp_rec())
    return temp_rec


@pytest.fixture(scope='function')
def temp_state():
    temp_rec = get_temp_rec()
    # Clean up any existing record first
    safe_delete(temp_rec)
    new_rec_id = qry.create(get_temp_rec())
    yield new_rec_id
    safe_delete(temp_rec)


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_count():
    assert qry.num_states() == len(qry.cache)


def test_count():
    # Clean up any existing state first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    # get the count
    old_count = qry.num_states()
    # add a record
    qry.create(get_temp_rec())
    assert qry.num_states() == old_count + 1
    safe_delete(temp_rec)


def test_good_create():
    # Clean up any existing state first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    old_count = qry.num_states()
    new_rec_id = qry.create(get_temp_rec())
    assert qry.is_valid_id(new_rec_id)
    assert qry.num_states() == old_count + 1
    safe_delete(temp_rec)


def test_create_dup_key():
    # Clean up any existing state first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    qry.create(get_temp_rec())
    with pytest.raises(ValueError):
        qry.create(get_temp_rec())
    safe_delete(temp_rec)


def test_create_bad_name():
    with pytest.raises(ValueError):
        qry.create({})


def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)


def test_delete(temp_state_no_del):
    ret = qry.delete(temp_state_no_del[qry.CODE],
                     temp_state_no_del[qry.COUNTRY_CODE])
    assert ret == 1


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some state code that is not there', 'not a country code')


def test_read(temp_state):
    states = qry.read()
    assert isinstance(states, dict)
    assert qry.SAMPLE_KEY in states

def test_create_missing_fields():
    bad = {qry.CODE: "NY"}  # missing COUNTRY_CODE
    with pytest.raises(ValueError):
        qry.create(bad)

def test_read_after_delete(temp_state):
    rec_id = temp_state
    temp_rec = get_temp_rec()
    qry.delete(temp_rec[qry.CODE], temp_rec[qry.COUNTRY_CODE])
    states = qry.read()
    key = f'{temp_rec[qry.CODE]},{temp_rec[qry.COUNTRY_CODE]}'
    assert key not in states

def test_create_returns_unique_ids():
    # Clean up any existing states first
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    safe_delete({'code': 'CA', 'country_code': 'USA'})
    
    rec1 = get_temp_rec()
    # Create first state
    id1 = qry.create(rec1)
    # Try to create the same state again - should fail due to duplicate key
    with pytest.raises(ValueError, match='Duplicate key'):
        qry.create(rec1)
    
    # Clean up
    safe_delete(temp_rec)
    
    # Now create two different states to verify unique IDs
    rec1 = get_temp_rec()
    rec2 = get_temp_rec()
    rec2[qry.CODE] = 'CA'  # Different code
    rec2[qry.NAME] = 'California'
    
    # Clean up these too
    safe_delete(rec1)
    safe_delete(rec2)
    
    id1 = qry.create(rec1)
    id2 = qry.create(rec2)
    
    assert id1 != id2
    
    # Clean up
    safe_delete(rec1)
    safe_delete(rec2)

def test_delete_then_delete_again(temp_state_no_del):
    """Ensure deleting a state twice raises ValueError the second time."""
    code = temp_state_no_del[qry.CODE]
    country = temp_state_no_del[qry.COUNTRY_CODE]
    # First delete should work
    ret = qry.delete(code, country)
    assert ret == 1
    # Second delete should raise ValueError
    with pytest.raises(ValueError):
        qry.delete(code, country)

def test_create_same_name_different_code():
    """States with the same NAME but different CODEs should be allowed."""
    # Clean up any existing states
    temp_rec = get_temp_rec()
    safe_delete(temp_rec)
    safe_delete({'code': 'CA', 'country_code': 'USA'})

    rec1 = get_temp_rec()
    rec2 = get_temp_rec()
    rec2[qry.CODE] = 'CA'  # Different code
    # Both have the same NAME
    rec2[qry.NAME] = rec1[qry.NAME]

    id1 = qry.create(rec1)
    id2 = qry.create(rec2)

    assert id1 != id2  # IDs should be unique
    states = qry.read()
    key1 = f"{rec1[qry.CODE]},{rec1[qry.COUNTRY_CODE]}"
    key2 = f"{rec2[qry.CODE]},{rec2[qry.COUNTRY_CODE]}"
    assert key1 in states
    assert key2 in states

    # Cleanup
    safe_delete(rec1)
    safe_delete(rec2)
