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
        'callerid': 'callerid',
        'outcallerid': 'outcallerid',
        'loginclient': 'username',
        'passwdclient': 'password',
        'musiconhold': 'musiconhold',
        'mobilephonenumber': 'mobilephonenumber',
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
        source.callerid = model.determine_callerid()

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        source.callerid = model.determine_callerid()
        return source


class User(NewModel):

    MANDATORY = [
        'firstname',
    ]

    FIELDS = [
        'id',
        'firstname',
        'lastname',
        'callerid',
        'outcallerid',
        'username',
        'password',
        'musiconhold',
        'mobilephonenumber',
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
        self._build_callerid()
        return NewModel.to_user_data(self)

    def _build_callerid(self):
        try:
            self.callerid = self._generate_callerid()
        except AttributeError:
            return

    @property
    def fullname(self):
        if not self.lastname:
            self.lastname = ''
        return ' '.join([self.firstname, self.lastname])

    def determine_callerid(self):
        return self._generate_callerid()

    def _generate_callerid(self):
        return '"%s"' % self.fullname


class UserOrdering(object):
    firstname = 'firstname'
    lastname = 'lastname'


db_converter = UserDbConverter()
