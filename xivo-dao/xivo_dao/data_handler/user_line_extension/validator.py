# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementNotExistsError, NonexistentParametersError

from xivo_dao.data_handler.context import services as context_services
from xivo_dao.data_handler.context.services import ContextRange
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user_line_extension import dao as ule_dao


def validate_create(ule):
    user, line, extension = validate(ule)
    check_if_user_and_line_already_linked(user, line)
    check_if_extension_in_context_range(extension)
    check_if_extension_already_linked_to_a_line(extension)
    return user, line, extension


def validate(ule):
    _check_missing_parameters(ule)
    _check_invalid_parameters(ule)
    user, line, extension = _get_secondary_associations(ule)
    return user, line, extension


def is_allowed_to_delete(ule):
    if ule.main_user is True and not ule_dao.main_user_is_allowed_to_delete(ule.line_id):
        raise InvalidParametersError(['There are secondary users associated to this link'])


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
    if hasattr(ule_id, 'main_user') and not isinstance(ule_id.main_user, bool):
        invalid_parameters.append('main_user must be bool')
    if hasattr(ule_id, 'main_line') and not isinstance(ule_id.main_line, bool):
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


def check_if_user_and_line_already_linked(user, line):
    if ule_dao.already_linked(user.id, line.id):
        raise InvalidParametersError(['user is already associated to this line'])


def check_if_extension_in_context_range(extension):
    if not context_services.is_extension_in_specific_range(extension, ContextRange.users):
        raise InvalidParametersError(['Exten %s not inside user range of context %s' % (extension.exten, extension.context)])


def check_if_extension_already_linked_to_a_line(extension):
    extensions = ule_dao.find_all_by_extension_id(extension.id)
    if len(extensions) > 0:
        raise InvalidParametersError(['Extension %s@%s already linked to a line' % (extension.exten, extension.context)])
