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
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema


class Voicemail(NewModel):

    MANDATORY = [
        'name',
        'number',
        'context'
    ]

    FIELDS = [
        'id',
        'name',
        'number',
        'context',
        'password',
        'email',
        'language',
        'timezone',
        'max_messages',
        'attach_audio',
        'delete_messages',
        'ask_password'
    ]

    SEARCH_COLUMNS = [
        VoicemailSchema.fullname,
        VoicemailSchema.mailbox,
        VoicemailSchema.email
    ]

    _RELATION = {
        'user': 'user'
    }

    @property
    def number_at_context(self):
        return '%s@%s' % (self.number, self.context)


class VoicemailDBConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'uniqueid': 'id',
        'fullname': 'name',
        'mailbox': 'number',
        'context': 'context',
        'password': 'password',
        'email': 'email',
        'language': 'language',
        'tz': 'timezone',
        'maxmsg': 'max_messages',
        'attach': 'attach_audio',
        'deletevoicemail': 'delete_messages',
        'skipcheckpass': 'ask_password'
    }

    def __init__(self):
        DatabaseConverter.__init__(self, self.DB_TO_MODEL_MAPPING, VoicemailSchema, Voicemail)

    def to_model(self, source):
        model = DatabaseConverter.to_model(self, source)
        self._convert_model_fields(model)

        return model

    def _convert_model_fields(self, model):
        model.attach_audio = bool(model.attach_audio)
        model.delete_messages = bool(model.delete_messages)
        model.ask_password = bool(model.ask_password)

        if model.password == '':
            model.password = None

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        self._convert_source_fields(source)

        return source

    def update_source(self, source, model):
        DatabaseConverter.update_source(self, source, model)
        self._convert_source_fields(source)

    def _convert_source_fields(self, source):
        if source.attach is not None:
            source.attach = int(bool(source.attach))
        if source.deletevoicemail is not None:
            source.deletevoicemail = int(bool(source.deletevoicemail))
        if source.skipcheckpass is not None:
            source.skipcheckpass = int(bool(source.skipcheckpass))
        if source.password is None:
            source.password = ''

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        if source.attach is not None:
            source.attach = int(bool(source.attach))
        if source.deletevoicemail is not None:
            source.deletevoicemail = int(bool(source.deletevoicemail))
        if source.skipcheckpass is not None:
            source.skipcheckpass = int(bool(source.skipcheckpass))

        return source


db_converter = VoicemailDBConverter()


class VoicemailOrder(object):
    name = VoicemailSchema.fullname
    number = VoicemailSchema.mailbox
    context = VoicemailSchema.context
    email = VoicemailSchema.email
    language = VoicemailSchema.language
    timezone = VoicemailSchema.tz
