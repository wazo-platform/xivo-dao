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

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema


class UserDbConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'id': 'id',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'callerid': 'caller_id',
        'outcallerid': 'outgoing_caller_id',
        'loginclient': 'username',
        'passwdclient': 'password',
        'musiconhold': 'music_on_hold',
        'mobilephonenumber': 'mobile_phone_number',
        'userfield': 'userfield',
        'timezone': 'timezone',
        'language': 'language',
        'description': 'description',
        'voicemailid': 'voicemail_id',
        'preprocess_subroutine': 'preprocess_subroutine',
    }

    def __init__(self):
        DatabaseConverter.__init__(self, self.DB_TO_MODEL_MAPPING, UserSchema, User)

    def update_source(self, source, model):
        DatabaseConverter.update_source(self, source, model)
        source.callerid = model.generate_caller_id()

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        source.callerid = model.generate_caller_id()
        return source


class User(NewModel):

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
    ]

    _RELATION = {
        'voicemailid': 'voicemail_id'
    }

    def to_user_data(self):
        self.caller_id = self.generate_caller_id()
        return NewModel.to_user_data(self)

    @property
    def fullname(self):
        if not self.lastname:
            self.lastname = ''
        return ' '.join([self.firstname, self.lastname])

    def generate_caller_id(self):
        return '"%s"' % self.determine_caller_id()

    def determine_caller_id(self):
        if self.caller_id:
            return self.clean_caller_id()
        return self.fullname

    def clean_caller_id(self):
        return self.caller_id.strip('"')


class UserOrdering(object):
    firstname = 'firstname'
    lastname = 'lastname'


db_converter = UserDbConverter()
