# To run test: PYTHONPATH=$(pwd) pytest -v cities/tests/test_queries.py

from unittest.mock import patch

import pytest

import cities.queries as qry


@pytest.fixture(scope='function')
def temp_city():
    new_rec_id = qry.create(qry.SAMPLE_CITY)
    yield new_rec_id
    try:
        qry.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')

    
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
    assert qry.is_valid_id(new_rec_id)
    # assert qry.num_cities() == old_count + 1

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
        assert 'country' in data
        assert 'population' in data

def test_create_duplicate_city():
    rec_id1 = qry.create(qry.SAMPLE_CITY)
    rec_id2 = qry.create(qry.SAMPLE_CITY)
    assert rec_id1 != rec_id2
    qry.delete(rec_id1)
    qry.delete(rec_id2)
