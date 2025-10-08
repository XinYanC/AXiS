
"""
This file deals with our city-level data.
"""

SUCCESS = 0
NAME = 'name'
STATE_CODE = 'state_code'

cities = {}

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
}


def create(flds: str):
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    return SUCCESS