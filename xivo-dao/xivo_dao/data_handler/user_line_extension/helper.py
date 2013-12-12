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

from xivo import caller_id
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user import dao as user_dao


def delete_association_if_necessary(session):
    query = (session.query(UserLineSchema)
             .filter(UserLineSchema.user_id == None)
             .filter(UserLineSchema.extension_id == None))
    query.delete()


def make_associations(main_user_id, line_id, extension_id):
    main_user = user_dao.get(main_user_id)
    line = line_dao.get(line_id)
    extension = extension_dao.find(extension_id) if extension_id else None
    exten = extension.exten if extension else None

    line.callerid = caller_id.assemble_caller_id(main_user.fullname, exten)

    if extension:
        extension_dao.associate_to_user(main_user, extension)
        line.number = extension.exten
        line.context = extension.context
        line_dao.update_xivo_userid(line, main_user)

    line_dao.edit(line)


def delete_associations(line_id, extension_id):
    raise NotImplementedError()
