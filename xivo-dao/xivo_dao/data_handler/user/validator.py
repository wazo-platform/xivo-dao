# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import ElementDeletionError

from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user_line import dao as user_line_dao
from xivo_dao.data_handler.user_voicemail import dao as user_voicemail_dao


def validate_create(user):
    validate_model(user)


def validate_edit(user):
    validate_model(user)


def validate_delete(user):
    validate_user_exists(user)
    validate_user_not_associated(user)


def validate_model(user):
    _check_missing_parameters(user)
    _check_invalid_parameters(user)


def _check_missing_parameters(user):
    missing = user.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(user):
    invalid_parameters = []
    if not user.firstname:
        invalid_parameters.append('firstname')
    if user.mobile_phone_number is not None and not unicode(user.mobile_phone_number).isnumeric():
        invalid_parameters.append('mobile_phone_number')
    if user.password is not None and len(user.password) < 4:
        invalid_parameters.append('password')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def validate_user_not_associated(user):
    validate_not_associated_to_voicemail(user)
    validate_not_associated_to_line(user)


def validate_not_associated_to_line(user):
    user_lines = user_line_dao.find_all_by_user_id(user.id)
    if user_lines:
        raise ElementDeletionError('User', 'user still associated to a line')


def validate_user_exists(user):
    user_dao.get(user.id)


def validate_not_associated_to_voicemail(user):
    user_voicemail = user_voicemail_dao.find_by_user_id(user.id)
    if user_voicemail:
        raise ElementDeletionError('User', 'user still associated to a voicemail')
