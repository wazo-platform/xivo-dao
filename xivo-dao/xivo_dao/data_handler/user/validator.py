# -*- coding: utf-8 -*-

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

from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import InvalidParametersError


def validate_create(user):
    validate_model(user)


def validate_edit(user):
    validate_model(user)


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
    if user.mobilephonenumber is not None and not unicode(user.mobilephonenumber).isnumeric():
        invalid_parameters.append('mobilephonenumber')
    if user.password is not None and len(user.password) < 4:
        invalid_parameters.append('password')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)
