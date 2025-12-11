from copy import deepcopy

from unittest.mock import patch
import pytest

import states.queries as qry


def get_temp_rec():
    return deepcopy(qry.SAMPLE_STATE)


@pytest.fixture(scope='function')
def temp_state_no_del():
    temp_rec = get_temp_rec()
    qry.create(get_temp_rec())
    return temp_rec


@pytest.fixture(scope='function')
def temp_state():
    temp_rec = get_temp_rec()
    new_rec_id = qry.create(get_temp_rec())
    yield new_rec_id
    try:
        qry.delete(temp_rec[qry.CODE], temp_rec[qry.COUNTRY_CODE])
    except ValueError:
        print('The record was already deleted.')


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_count():
    assert qry.num_states() == len(qry.cache)


def test_count():
    # Clean up any existing state first
    try:
        qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)
    except ValueError:
        pass  # State doesn't exist, which is fine
    # get the count
    old_count = qry.num_states()
    # add a record
    qry.create(get_temp_rec())
    assert qry.num_states() == old_count + 1
    qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)


def test_good_create():
    # Clean up any existing state first
    try:
        qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)
    except ValueError:
        pass  # State doesn't exist, which is fine
    old_count = qry.num_states()
    new_rec_id = qry.create(get_temp_rec())
    assert qry.is_valid_id(new_rec_id)
    assert qry.num_states() == old_count + 1
    qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)


def test_create_dup_key():
    # Clean up any existing state first
    try:
        qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)
    except ValueError:
        pass  # State doesn't exist, which is fine
    qry.create(get_temp_rec())
    with pytest.raises(ValueError):
        qry.create(get_temp_rec())
    qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)


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
    try:
        qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)
    except ValueError:
        pass  # Doesn't exist, which is fine
    try:
        qry.delete('CA', 'USA')
    except ValueError:
        pass  # Doesn't exist, which is fine
    
    rec1 = get_temp_rec()
    # Create first state
    id1 = qry.create(rec1)
    # Try to create the same state again - should fail due to duplicate key
    with pytest.raises(ValueError, match='Duplicate key'):
        qry.create(rec1)
    
    # Clean up
    qry.delete(qry.SAMPLE_CODE, qry.SAMPLE_COUNTRY)
    
    # Now create two different states to verify unique IDs
    rec1 = get_temp_rec()
    rec2 = get_temp_rec()
    rec2[qry.CODE] = 'CA'  # Different code
    rec2[qry.NAME] = 'California'
    
    id1 = qry.create(rec1)
    id2 = qry.create(rec2)
    
    assert id1 != id2
    
    # Clean up
    qry.delete(rec1[qry.CODE], rec1[qry.COUNTRY_CODE])
    qry.delete(rec2[qry.CODE], rec2[qry.COUNTRY_CODE])
