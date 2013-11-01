# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
from converters.database_converter import DatabaseConverter

from xivo_dao.helpers.new_model import NewModel

DB_TO_MODEL_MAPPING = {
    'user_id': 'user_id',
    'voicemail_id': 'voicemail_id'
}


class UserVoicemail(NewModel):

    FIELDS = [
        'user_id',
        'voicemail_id'
    ]

    MANDATORY = [
        'user_id',
        'voicemail_id',
    ]

    _RELATION = {}


db_converter = DatabaseConverter(DB_TO_MODEL_MAPPING, None, UserVoicemail)