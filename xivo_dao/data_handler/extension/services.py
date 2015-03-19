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

from . import dao
from . import notifier

from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.line import dao as line_dao

from xivo_dao.data_handler.extension import validator


def get(extension_id):
    return dao.get(extension_id)


def get_by_exten_context(exten, context):
    return dao.get_by_exten_context(exten, context)


def search(**parameters):
    return dao.search(**parameters)


def find_by_exten(exten, order=None):
    return dao.find_by_exten(exten, order=None)


def find_by_context(context, order=None):
    return dao.find_by_context(context, order=None)


def find_by_exten_context(exten, context):
    return dao.find_by_exten_context(exten, context)


def create(extension):
    validator.validate_create(extension)
    extension = dao.create(extension)
    notifier.created(extension)
    return extension


def edit(extension):
    validator.validate_edit(extension)
    dao.edit(extension)
    line_extension = line_extension_dao.find_by_extension_id(extension.id)
    if line_extension:
        line_dao.associate_extension(extension, line_extension.line_id)
    notifier.edited(extension)


def delete(extension):
    validator.validate_delete(extension)
    dao.delete(extension)
    notifier.deleted(extension)
