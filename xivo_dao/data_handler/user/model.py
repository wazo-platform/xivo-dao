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

from xivo_dao.helpers.new_model import NewModel


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
    ]

    _RELATION = {
        'voicemailid': 'voicemail_id'
    }

    def to_user_data(self):
        user_data = NewModel.to_user_data(self)
        user_data['caller_id'] = self.generate_caller_id()
        return user_data

    @property
    def fullname(self):
        if not self.lastname:
            self.lastname = ''
        return ' '.join([self.firstname, self.lastname])

    def update_caller_id(self, original):
        if self.cleaned_caller_id() != original.cleaned_caller_id():
            self.caller_id = self.cleaned_caller_id()
        elif self.fullname != original.fullname:
            self.caller_id = self.caller_id_from_fullname()
        else:
            self.caller_id = self.cleaned_caller_id()

    def cleaned_caller_id(self):
        return '"%s"' % self.caller_id.strip('"')

    def caller_id_from_fullname(self):
        return '"%s"' % self.fullname

    def generate_caller_id(self):
        if self.caller_id:
            return self.cleaned_caller_id()
        return self.caller_id_from_fullname()


class UserDirectoryView(NewModel):
    __name__ = 'user'

    FIELDS = [
        'id',
        'line_id',
        'agent_id',
        'firstname',
        'lastname',
        'exten',
        'mobile_phone_number'
    ]
    _RELATION = {}
