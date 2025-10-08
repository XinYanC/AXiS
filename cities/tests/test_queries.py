# To run test: PYTHONPATH=$(pwd) pytest -v cities/tests/test_queries.py

import pytest

import cities.queries as qry


def test_good_create():
    assert qry.create(qry.SAMPLE_CITY) == qry.SUCCESS


def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)