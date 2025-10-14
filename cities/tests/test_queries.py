# To run test: PYTHONPATH=$(pwd) pytest -v cities/tests/test_queries.py

import pytest

import cities.queries as qry


def test_good_create():
    old_rec_count = len(qry.cities)
    assert qry.create(qry.SAMPLE_CITY) >= 1
    assert len(qry.cities) > old_rec_count


def test_create_bad_name():
    with pytest.raises(ValueError):
        qry.create({})

def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)