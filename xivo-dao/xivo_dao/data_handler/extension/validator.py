# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from xivo_dao.data_handler.exception import ElementAlreadyExistsError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.context import services as context_services


def validate_create(extension):
    _validate(extension)


def validate_edit(extension):
    _validate(extension)


def validate_delete(extension):
    validate_extension_exists(extension)
    validate_not_associated_to_line(extension)


def _validate(extension):
    validate_invalid_parameters(extension)
    validate_missing_parameters(extension)
    validate_context_exists(extension)
    validate_extension_available(extension)
    validate_extension_in_range(extension)


def validate_invalid_parameters(extension):
    if not extension.exten:
        raise InvalidParametersError(['Exten required'])
    if not extension.context:
        raise InvalidParametersError(['Context required'])
    if extension.commented not in [True, False]:
        raise InvalidParametersError(['Commented must be a bool'])


def validate_missing_parameters(extension):
    missing = extension.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def validate_context_exists(extension):
    existing_context = context_services.find_by_name(extension.context)
    if not existing_context:
        raise NonexistentParametersError(context=extension.context)


def validate_extension_available(extension):
    existing_extension = extension_dao.find_by_exten_context(extension.exten, extension.context)
    if existing_extension:
        exten_context = '%s@%s' % (extension.exten, extension.context)
        raise ElementAlreadyExistsError('Extension', exten_context)


def validate_extension_in_range(extension):
    if not context_services.is_extension_valid_for_context(extension):
        raise InvalidParametersError(['exten %s not inside range of context %s' % (
            extension.exten,
            extension.context)])


def validate_extension_exists(extension):
    extension_dao.get(extension.id)


def validate_not_associated_to_line(extension):
    line_extension = line_extension_dao.find_by_extension_id(extension.id)
    if line_extension:
        raise ElementDeletionError('Extension', 'extension still has a link')
