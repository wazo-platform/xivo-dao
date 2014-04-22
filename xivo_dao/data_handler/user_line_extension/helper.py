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

from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.line import dao as line_dao


def delete_extension_associations(extension_id):
    extension = extension_dao.get(extension_id)
    line_dao.dissociate_extension(extension)
    extension_dao.dissociate_extension(extension)


def validate_no_device(line_id):
    line = line_dao.get(line_id)
    if line.device_id:
        raise InvalidParametersError(['A device is still associated to the line'])
