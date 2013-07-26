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

from . import dao
from . import notifier

from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementNotExistsError
from xivo_dao.data_handler.line import services as line_services


def get(extension_id):
    return dao.get(extension_id)


def get_by_exten_context(exten, context):
    return dao.get_by_exten_context(exten, context)


def get_by_type_typeval(type, typeval):
    return dao.get_by_type_typeval(type, typeval)


def find_all(order=None):
    return dao.find_all(order=order)


def find_by_exten(exten, order=None):
    return dao.find_by_exten(exten, order=None)


def find_by_context(context, order=None):
    return dao.find_by_context(context, order=None)


def create(extension):
    _validate(extension)
    extension = dao.create(extension)
    notifier.created(extension)
    return extension


def edit(extension):
    _validate(extension)
    dao.edit(extension)
    notifier.edited(extension)


def delete(extension):
    dao.delete(extension)
    _remove_exten_from_line_schema(extension)
    notifier.deleted(extension)


def _validate(extension):
    _check_missing_parameters(extension)
    _check_invalid_parameters(extension)


def _check_missing_parameters(extension):
    missing = extension.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(extension):
    invalid_parameters = []
    if len(str(extension.exten)) == 0:
        invalid_parameters.append('Exten required')
    if len(extension.context) == 0:
        invalid_parameters.append('Context required')
    if len(extension.type) == 0:
        invalid_parameters.append('Type required')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _remove_exten_from_line_schema(extension):
    try:
        line = line_services.get_by_number_context(extension.exten, extension.context)
        line.number = ''
        line.context = ''
        line.provisioningid = 0
        line_services.edit(line)
    except ElementNotExistsError:
        return
