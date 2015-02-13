# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao import context_dao as old_context_dao
from xivo_dao.data_handler.context import dao as context_dao
from xivo_dao.data_handler import errors
from xivo_dao.data_handler.context import validator
from xivo_dao.data_handler.context import notifier


def find_by_name(context_name):
    return old_context_dao.get(context_name)


def create(context):
    validator.validate_create(context)
    created_context = context_dao.create(context)
    notifier.created(created_context)
    return created_context


def is_extension_valid_for_context(extension):
    exten = _validate_exten(extension)
    context_ranges = context_dao.find_all_context_ranges(extension.context)
    return is_extension_included_in_ranges(exten, context_ranges)


def _validate_exten(extension):
    if not extension.exten.isdigit():
        raise errors.wrong_type('exten', 'numeric string')
    return extension.exten


def is_extension_included_in_ranges(exten, context_ranges):
    for context_range in context_ranges:
        if context_range.in_range(exten):
            return True
    return False


def is_extension_valid_for_context_range(extension, context_range):
    exten = _validate_exten(extension)
    context_ranges = context_dao.find_all_specific_context_ranges(extension.context, context_range)
    return is_extension_included_in_ranges(exten, context_ranges)
