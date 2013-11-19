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

from xivo_dao.data_handler.line_extension import dao
from xivo_dao.data_handler.line_extension import notifier
from xivo_dao.data_handler.line_extension import validator


def associate(line_extension):
    validator.validate_associate(line_extension)
    line_extension = dao.associate(line_extension)
    notifier.associated(line_extension)
    return line_extension


def get_by_line_id(line_id):
    return dao.get_by_line_id(line_id)


def dissociate(line_extension):
    validator.validate_dissociation(line_extension)
    dao.dissociate(line_extension)
    notifier.dissociated(line_extension)
    return line_extension
