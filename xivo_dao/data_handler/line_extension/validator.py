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

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.context.model import ContextType
from xivo_dao.data_handler.context import dao as context_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.extension import validator as extension_validator
from xivo_dao.data_handler.incall import dao as incall_dao
from xivo_dao.data_handler.user_line import dao as user_line_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.user_line_extension import helper as ule_helper


def validate_associate(line_extension):
    validate_model(line_extension)
    validate_line(line_extension)
    validate_extension(line_extension)
    validate_context_type_on_association(line_extension)


def validate_model(line_extension):
    missing = line_extension.missing_parameters()
    if len(missing) > 0:
        raise MissingParametersError(missing)


def validate_line(line_extension):
    try:
        line_dao.get(line_extension.line_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(line_id=line_extension.line_id)


def validate_extension(line_extension):
    try:
        return extension_dao.get(line_extension.extension_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(extension_id=line_extension.extension_id)


def validate_context_type_on_association(line_extension):
    context = context_dao.get_by_extension_id(line_extension.extension_id)
    if context.type == ContextType.internal:
        validate_line_not_associated_to_extension(line_extension)
        extension_validator.validate_extension_not_associated(line_extension.extension_id)
    elif context.type == ContextType.incall:
        validate_associated_to_user(line_extension)
    else:
        msg = "extension with a context of type '%s' cannot be associated to a line"
        raise InvalidParametersError([msg % context.type])


def validate_line_not_associated_to_extension(line_extension):
    line_extension = line_extension_dao.find_by_line_id(line_extension.line_id)
    if line_extension:
        msg = "line with id %s already has an extension with a context of type 'internal'"
        raise InvalidParametersError([msg % line_extension.line_id])


def validate_associated_to_user(line_extension):
    user_lines = user_line_dao.find_all_by_line_id(line_extension.line_id)
    if not user_lines:
        msg = 'line with id %s is not associated to a user'
        raise InvalidParametersError([msg % line_extension.line_id])


def validate_dissociation(line_extension):
    validate_extension(line_extension)
    validate_line(line_extension)
    validate_associated(line_extension)
    validate_context_type_on_dissociation(line_extension)


def validate_context_type_on_dissociation(line_extension):
    context = context_dao.get_by_extension_id(line_extension.extension_id)
    if context.type == ContextType.internal:
        ule_helper.validate_no_device(line_extension.line_id)


def validate_associated(line_extension):
    line_extensions = _all_line_extensions(line_extension.line_id)
    if line_extension not in line_extensions:
        msg = 'Line (id=%s) is not associated with Extension (id=%s)'
        raise InvalidParametersError([msg % (line_extension.line_id, line_extension.extension_id)])


def _all_line_extensions(line_id):
    return (line_extension_dao.find_all_by_line_id(line_id)
            + incall_dao.find_all_line_extensions_by_line_id(line_id))
