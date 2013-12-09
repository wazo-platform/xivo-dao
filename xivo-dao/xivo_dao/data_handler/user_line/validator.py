# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError, NonexistentParametersError, InvalidParametersError
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user_line import dao as user_line_dao


def validate_association(user_line):
    _validate_missing_parameters(user_line)
    _validate_invalid_parameters(user_line)
    _validate_user_id(user_line)
    _validate_line_id(user_line)
    _validate_user_not_associated_with_line(user_line)


def validate_dissociation(user_line):
    _validate_user_id(user_line)
    _validate_line_id(user_line)
    _validate_user_has_line(user_line)
    _is_allowed_to_dissociate(user_line)


def _validate_missing_parameters(user_line):
    missing = user_line.missing_parameters()
    if len(missing) > 0:
        raise MissingParametersError(missing)


def _validate_invalid_parameters(user_line):
    invalid_parameters = []
    if not isinstance(user_line.user_id, int):
        invalid_parameters.append('user_id must be integer')
    if not isinstance(user_line.line_id, int):
        invalid_parameters.append('line_id must be integer')
    if hasattr(user_line, 'main_user') and not isinstance(user_line.main_user, bool):
        invalid_parameters.append('main_user must be boolean')
    if hasattr(user_line, 'main_line') and not isinstance(user_line.main_line, bool):
        invalid_parameters.append('main_line must be boolean')

    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _validate_user_id(user_line):
    try:
        return user_dao.get(user_line.user_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(user_id=user_line.user_id)


def _validate_line_id(user_line):
    try:
        return line_dao.get(user_line.line_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(line_id=user_line.line_id)


def _validate_user_has_line(user_line):
    user_lines = user_line_dao.find_all_by_user_id(user_line.user_id)
    if len(user_lines) == 0:
        raise InvalidParametersError(['user with id %s does not have any line' % user_line.user_id])


def _validate_user_not_associated_with_line(user_line):
    try:
        user_line_dao.get_by_user_id_and_line_id(user_line.user_id, user_line.line_id)
    except ElementNotExistsError:
        pass
    else:
        raise InvalidParametersError(['user is already associated to this line'])


def _is_allowed_to_dissociate(user_line):
    if user_line.main_user is True and user_line_dao.line_has_secondary_user(user_line):
        raise InvalidParametersError(['There are secondary users associated to this line'])
