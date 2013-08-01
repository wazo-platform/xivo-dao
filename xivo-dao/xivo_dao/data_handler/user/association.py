# -*- coding: utf-8 -*-
#
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

from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.user_line_extension import services as ule_services
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension


def associate_voicemail(user_id, voicemail_id):
    user = user_services.get(user_id)
    voicemail = voicemail_services.get(voicemail_id)
    user.voicemail_id = voicemail.id
    user_services.edit(user)


def associate_user_line_extension(user_id, line_id, extension_id, main_user=True, main_line=True):
    user = user_services.get(user_id)
    line = line_services.get(line_id)
    extension = extension_services.get(extension_id)

    ule = UserLineExtension(user_id=user.id,
                            line_id=line.id,
                            extension_id=extension.id,
                            main_user=main_user,
                            main_line=main_line)

    ule_services.create(ule)

    line_dao.associate_extension(extension, line.id)

    extension.type = 'user'
    extension.typeval = str(user.id)
    extension_dao.edit(extension)

    return ule
