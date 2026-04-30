import pytest

import data.email_address as ea


def test_abc_base_not_instantiable():
    with pytest.raises(TypeError):
        ea.EmailAddress('user@example.com')


def test_construct_standard_email():
    addr = ea.StandardEmailAddress('user@example.com')
    assert isinstance(addr, ea.StandardEmailAddress)
    assert str(addr) == 'user@example.com'


def test_construct_standard_email_normalizes_case_and_spaces():
    addr = ea.StandardEmailAddress('  First.Last+tag@Example.EDU  ')
    assert str(addr) == 'first.last+tag@example.edu'


def test_construct_standard_email_bad_type():
    with pytest.raises(TypeError):
        ea.StandardEmailAddress(42)


def test_construct_standard_email_empty():
    with pytest.raises(ValueError):
        ea.StandardEmailAddress('   ')


def test_construct_standard_email_missing_at_sign():
    with pytest.raises(ValueError):
        ea.StandardEmailAddress('user.example.com')


def test_construct_standard_email_bad_domain():
    with pytest.raises(ValueError):
        ea.StandardEmailAddress('user@localhost')


def test_construct_edu_email_valid():
    addr = ea.EduEmailAddress('student@school.edu')
    assert isinstance(addr, ea.EduEmailAddress)
    assert str(addr) == 'student@school.edu'


def test_construct_edu_email_rejects_non_edu():
    with pytest.raises(ValueError):
        ea.EduEmailAddress('student@gmail.com')
