"""
Form metadata for endpoint-driven dropdowns (HATEOAS-style discovery).
"""

import examples.form_filler as ff

from examples.form_filler import FLD_NM  # for tests

COUNTRY = 'country'
STATE = 'state'
CITY = 'city'
TRANSACTION_TYPE = 'transaction_type'

DROPDOWN_FORM_FLDS = [
    {
        FLD_NM: 'Instructions',
        ff.QSTN: 'Select options from endpoint-provided dropdown values.',
        ff.INSTRUCTIONS: True,
    },
    {
        FLD_NM: COUNTRY,
        ff.QSTN: 'Country:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: True,
        ff.CHOICES: 'GET /system/dropdown-options -> countries',
    },
    {
        FLD_NM: STATE,
        ff.QSTN: 'State:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: True,
        ff.CHOICES: (
            'GET /system/dropdown-options?country_code=<code> -> states'
        ),
    },
    {
        FLD_NM: CITY,
        ff.QSTN: 'City:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: True,
        ff.CHOICES: (
            'GET /system/dropdown-options?state_code=<code> -> cities'
        ),
    },
    {
        FLD_NM: TRANSACTION_TYPE,
        ff.QSTN: 'Transaction type:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: True,
        ff.CHOICES: ['free', 'sell'],
    },
]


def get_form() -> list:
    return DROPDOWN_FORM_FLDS


def get_form_descr() -> dict:
    return ff.get_form_descr(DROPDOWN_FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(DROPDOWN_FORM_FLDS)
