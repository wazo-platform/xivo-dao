import dao as ule_dao

from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementNotExistsError, NonexistentParametersError

from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user import dao as user_dao


def validate(ule):
    _check_missing_parameters(ule)
    _check_invalid_parameters(ule)
    user, line, extension = _get_secondary_associations(ule)
    _check_if_already_linked(user, line)
    return user, line, extension


def _check_missing_parameters(ule):
    missing = ule.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(ule_id):
    invalid_parameters = []
    if not isinstance(ule_id.user_id, int):
        invalid_parameters.append('user_id must be integer')
    if ule_id.user_id == 0:
        invalid_parameters.append('user_id equal to 0')
    if not isinstance(ule_id.line_id, int):
        invalid_parameters.append('line_id must be integer')
    if ule_id.line_id == 0:
        invalid_parameters.append('line_id equal to 0')
    if not isinstance(ule_id.extension_id, int):
        invalid_parameters.append('extension_id must be integer')
    if ule_id.extension_id == 0:
        invalid_parameters.append('extension_id equal to 0')
    if not isinstance(ule_id.main_user, bool):
        invalid_parameters.append('main_user must be bool')
    if not isinstance(ule_id.main_line, bool):
        invalid_parameters.append('main_line must be bool')

    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _get_secondary_associations(ule):
    nonexistent = {}

    try:
        extension = extension_dao.get(ule.extension_id)
    except ElementNotExistsError:
        nonexistent['extension_id'] = ule.extension_id

    try:
        line = line_dao.get(ule.line_id)
    except ElementNotExistsError:
        nonexistent['line_id'] = ule.line_id

    try:
        user = user_dao.get(ule.user_id)
    except ElementNotExistsError:
        nonexistent['user_id'] = ule.user_id

    if len(nonexistent) > 0:
        raise NonexistentParametersError(**nonexistent)

    return user, line, extension


def _check_if_already_linked(user, line):
    if ule_dao.already_linked(user.id, line.id):
        raise InvalidParametersError(['user is already associated to this line'])
