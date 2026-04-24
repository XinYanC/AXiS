from functools import wraps

# import data.db_connect as dbc

"""
Our record format to meet our requirements (see security.md) will be:

{
    feature_name1: {
        create: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        read: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        update: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        delete: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
    },
    feature_name2: # etc.
}
"""

COLLECT_NAME = 'security'
CREATE = 'create'
READ = 'read'
UPDATE = 'update'
DELETE = 'delete'
USER_LIST = 'user_list'
CHECKS = 'checks'
LOGIN = 'login'

# Features:
PEOPLE = 'people'

security_recs = None
# These will come from the DB soon:
temp_recs = {
    PEOPLE: {
        CREATE: {
            USER_LIST: ['ejc369@nyu.edu'],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
}


def read() -> dict:
    global security_recs
    # dbc.read()
    security_recs = temp_recs
    return security_recs


def needs_recs(fn):
    """
    Should be used to decorate any function that directly accesses sec recs.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global security_recs
        if not security_recs:
            security_recs = read()
        return fn(*args, **kwargs)
    return wrapper


@needs_recs
def read_feature(feature_name: str) -> dict:
    if feature_name in security_recs:
        return security_recs[feature_name]
    else:
        return None


def is_operation_allowed(
    feature_name: str,
    operation: str,
    *,
    authed_user_email: str | None,
    auth_valid: bool,
) -> tuple[str, str | None]:
    """
    Decide if an action on `feature_name` is allowed for `operation`
    (e.g. create, read).

    Identity is the caller's verified email (after a successful password
    check) when `auth_valid` is True. Use HTTP Basic auth in the
    application layer to obtain that.

    Returns
        ('ok', None) on allow.
        ('unauthorized', message) if authentication is required but
        missing or not verified.
        ('forbidden', message) if the caller is not permitted for this
        operation.
    """
    feature = read_feature(feature_name)
    if (
        not feature
        or not isinstance(feature, dict)
        or operation not in feature
    ):
        return 'ok', None
    op_cfg = feature[operation]
    if not isinstance(op_cfg, dict):
        return 'ok', None
    user_list = op_cfg.get(USER_LIST) or []
    checks = op_cfg.get(CHECKS) or {}
    login_req = bool(checks.get(LOGIN))
    has_allowlist = len(user_list) > 0
    need_auth = login_req or has_allowlist
    if need_auth and not auth_valid:
        return (
            'unauthorized',
            'This action requires identity verification. Use HTTP Basic '
            'Auth with your email and password (username: email, '
            'password: password).',
        )
    if not has_allowlist:
        return 'ok', None
    allowed = {
        e.strip().lower()
        for e in user_list
        if isinstance(e, str) and e.strip()
    }
    email_key = (authed_user_email or '').strip().lower()
    if not authed_user_email or email_key not in allowed:
        return (
            'forbidden',
            'Your account is not allowed to perform this action.',
        )
    return 'ok', None
