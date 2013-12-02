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

from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.exception import InvalidParametersError


def validate_associate(line_extension):
    validate_model(line_extension)
    validate_line(line_extension)
    validate_extension(line_extension)
    validate_not_associated_to_extension(line_extension)


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
        extension_dao.get(line_extension.extension_id)
    except ElementNotExistsError:
        raise NonexistentParametersError(extension_id=line_extension.extension_id)


def validate_not_associated_to_extension(line_extension):
    line_extension = line_extension_dao.find_by_line_id(line_extension.line_id)
    if line_extension:
        raise InvalidParametersError(['line with id %s already has an extension' % line_extension.line_id])


def validate_dissociation(line_extension):
    validate_extension(line_extension)
