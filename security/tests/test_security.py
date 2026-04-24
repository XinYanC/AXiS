import security.security as sec


def test_read():
    recs = sec.read()
    assert isinstance(recs, dict)
    for feature in recs:
        assert isinstance(feature, str)
        assert len(feature) > 0


def test_people_create_allowlisted_email():
    st, _ = sec.is_operation_allowed(
        sec.PEOPLE,
        sec.CREATE,
        authed_user_email='ejc369@nyu.edu',
        auth_valid=True,
    )
    assert st == 'ok'


def test_people_create_not_on_list():
    st, msg = sec.is_operation_allowed(
        sec.PEOPLE,
        sec.CREATE,
        authed_user_email='other@nyu.edu',
        auth_valid=True,
    )
    assert st == 'forbidden'
    assert msg


def test_people_create_requires_auth():
    st, msg = sec.is_operation_allowed(
        sec.PEOPLE,
        sec.CREATE,
        authed_user_email=None,
        auth_valid=False,
    )
    assert st == 'unauthorized'
    assert msg
