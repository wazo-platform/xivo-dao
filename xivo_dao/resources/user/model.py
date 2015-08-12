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

from xivo_dao.helpers.new_model import NewModel
from collections import namedtuple


class User(NewModel):
    __name__ = 'user'

    MANDATORY = [
        'firstname',
    ]

    FIELDS = [
        'id',
        'firstname',
        'lastname',
        'caller_id',
        'outgoing_caller_id',
        'username',
        'password',
        'music_on_hold',
        'mobile_phone_number',
        'userfield',
        'timezone',
        'language',
        'description',
        'preprocess_subroutine',
        'private_template_id',
        'func_key_template_id',
    ]

    _RELATION = {
        'voicemailid': 'voicemail_id'
    }

    @property
    def fullname(self):
        lastname = self.lastname or ''
        return ' '.join([self.firstname, lastname]).strip()


UserDirectory = namedtuple('UserDirectory', ('id',
                                             'line_id',
                                             'agent_id',
                                             'firstname',
                                             'lastname',
                                             'exten',
                                             'mobile_phone_number'))
