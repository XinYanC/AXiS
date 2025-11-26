import data.db_connect as dbc

VALID_ID = '1' * dbc.MIN_ID_LEN
INVALID_ID = '1' * (dbc.MIN_ID_LEN - 1)


def test_is_valid_id():
    assert dbc.is_valid_id(VALID_ID)


def test_is_not_valid_id():
    assert not dbc.is_valid_id(INVALID_ID)


def test_is_not_valid_id_bad_type():
    assert not dbc.is_valid_id(17)


def test_is_not_valid_id_empty_string():
    # Empty string should be invalid because length < MIN_ID_LEN
    assert not dbc.is_valid_id("")


def test_is_not_valid_id_none():
    # None should be invalid (not a string)
    assert not dbc.is_valid_id(None)