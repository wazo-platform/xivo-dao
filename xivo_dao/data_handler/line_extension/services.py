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

from xivo_dao.data_handler.context.model import ContextType
from xivo_dao.data_handler.incall.model import Incall
from xivo_dao.data_handler.context import dao as context_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.incall import dao as incall_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user_line import dao as user_line_dao
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.line_extension import notifier
from xivo_dao.data_handler.line_extension import validator
from xivo_dao.data_handler.user_line_extension import services as ule_services


def find_by_line_id(line_id):
    return line_extension_dao.find_by_line_id(line_id)


def get_by_line_id(line_id):
    line = line_dao.get(line_id)
    return line_extension_dao.get_by_line_id(line.id)


def find_by_extension_id(extension_id):
    return line_extension_dao.find_by_extension_id(extension_id)


def get_by_extension_id(extension_id):
    extension = extension_dao.get(extension_id)
    return line_extension_dao.get_by_extension_id(extension.id)


def get_all_by_line_id(line_id):
    line = line_dao.get(line_id)
    line_extensions = line_extension_dao.find_all_by_line_id(line.id)
    incalls = incall_dao.find_all_line_extensions_by_line_id(line.id)
    return line_extensions + incalls


def associate(line_extension):
    validator.validate_associate(line_extension)
    _create_association(line_extension)
    notifier.associated(line_extension)
    return line_extension


def _create_association(line_extension):
    context = context_dao.get_by_extension_id(line_extension.extension_id)
    if context.type == ContextType.internal:
        _create_internal_association(line_extension)
    elif context.type == ContextType.incall:
        _create_incall_association(line_extension)


def _create_internal_association(line_extension):
    ule_services.associate_line_extension(line_extension)


def _create_incall_association(line_extension):
    user_line = user_line_dao.find_main_user_line(line_extension.line_id)

    incall = Incall.user_destination(user_line.user_id,
                                     line_extension.extension_id)
    created_incall = incall_dao.create(incall)

    extension_dao.associate_destination(line_extension.extension_id, 'incall', created_incall.id)


def dissociate(line_extension):
    validator.validate_dissociation(line_extension)
    _delete_association(line_extension)
    notifier.dissociated(line_extension)
    return line_extension


def _delete_association(line_extension):
    context = context_dao.get_by_extension_id(line_extension.extension_id)
    if context.type == ContextType.internal:
        _delete_internal_association(line_extension)
    elif context.type == ContextType.incall:
        _delete_incall_association(line_extension)


def _delete_internal_association(line_extension):
    ule_services.dissociate_line_extension(line_extension)


def _delete_incall_association(line_extension):
    incall = incall_dao.find_by_extension_id(line_extension.extension_id)
    incall_dao.delete(incall)
    extension_dao.dissociate_extension(line_extension.extension_id)
