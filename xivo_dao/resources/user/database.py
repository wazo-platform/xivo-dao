# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from __future__ import unicode_literals

from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.resources.user.model import User


class UserDbConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'id': 'id',
        'firstname': 'firstname',
        'lastname': 'lastname',
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
        'func_key_private_template_id': 'private_template_id',
        'func_key_template_id': 'func_key_template_id',
        'callerid': 'caller_id',
    }

    def __init__(self):
        super(UserDbConverter, self).__init__(self.DB_TO_MODEL_MAPPING, UserSchema, User)

    def to_model(self, source):
        model = super(UserDbConverter, self).to_model(source)
        self._convert_model_fields(model)
        return model

    def _convert_model_fields(self, model):
        for field in ('password',
                      'mobile_phone_number',
                      'lastname',
                      'username',
                      'description',
                      'outgoing_caller_id',
                      'music_on_hold',
                      'mobile_phone_number',
                      'userfield'):
            if getattr(model, field) == '':
                setattr(model, field, None)

    def update_source(self, source, model):
        super(UserDbConverter, self).update_source(source, model)
        self._convert_source_fields(source, model)

    def to_source(self, model):
        source = super(UserDbConverter, self).to_source(model)
        self._convert_source_fields(source, model)
        return source

    def _convert_source_fields(self, source, model):
        for field in ('passwdclient',
                      'mobilephonenumber',
                      'lastname',
                      'loginclient',
                      'description',
                      'outcallerid',
                      'musiconhold',
                      'mobilephonenumber',
                      'userfield'):
            if getattr(source, field) is None:
                setattr(source, field, '')


db_converter = UserDbConverter()
