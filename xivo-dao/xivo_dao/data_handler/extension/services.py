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
    InvalidParametersError, ElementAlreadyExistsError, NonexistentParametersError

from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.context import services as context_services


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
    line_dao.unassociate_extension(extension)
    dao.delete(extension)
    notifier.deleted(extension)


def _validate(extension):
    _check_missing_parameters(extension)
    _check_invalid_parameters(extension)
    _check_if_extension_already_exists(extension)
    _check_if_context_exists(extension)
    _check_if_exten_in_range(extension)


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


def _check_if_extension_already_exists(extension):
    extension = dao.find_by_exten_context(extension.exten, extension.context)
    if extension:
        exten_context = '%s@%s' % (extension.exten, extension.context)
        raise ElementAlreadyExistsError('Extension', exten_context)


def _check_if_context_exists(extension):
    context = context_services.find_by_name(extension.context)
    if not context:
        raise NonexistentParametersError(context=extension.context)


def _check_if_exten_in_range(extension):
    if not context_services.is_extension_inside_range(extension):
        raise InvalidParametersError(['exten %s not inside range of context %s' % (
            extension.exten,
            extension.context)])
