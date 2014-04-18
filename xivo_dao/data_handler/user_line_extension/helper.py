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

from xivo import caller_id
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user_line import dao as user_line_dao


def make_associations(main_user_id, line_id, extension_id):
    main_user = user_dao.get(main_user_id)
    line = line_dao.get(line_id)
    extension = extension_dao.find(extension_id) if extension_id else None
    exten = extension.exten if extension else None

    line.callerid = caller_id.assemble_caller_id(main_user.fullname, exten)
    line_dao.edit(line)

    if extension:
        extension_dao.associate_to_user(main_user, extension)
        line_dao.associate_extension(extension, line.id)
        line_dao.update_xivo_userid(line, main_user)


def make_line_extension_associations(line_extension):
    main_user_line = user_line_dao.find_main_user_line(line_extension.line_id)
    if main_user_line:
        make_associations(main_user_line.user_id,
                          line_extension.line_id,
                          line_extension.extension_id)


def delete_extension_associations(line_id, extension_id):
    extension = extension_dao.get(extension_id)
    line_dao.dissociate_extension(extension)
    extension_dao.dissociate_extension(extension)


def validate_no_device(line_id):
    line = line_dao.get(line_id)
    if line.device_id:
        raise InvalidParametersError(['A device is still associated to the line'])
