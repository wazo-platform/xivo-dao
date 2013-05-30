# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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


class User(object):

    _FIELDS = [
        'id',
        'firstname',
        'lastname',
        'callerid',
        'ringseconds',
        'simultcalls',
        'enablevoicemail',
        'voicemailid',
        'enablexfer',
        'enableautomon',
        'callrecord',
        'incallfilter',
        'enablednd',
        'enableunc',
        'destunc',
        'enablerna',
        'destrna',
        'enablebusy',
        'destbusy',
        'musiconhold',
        'outcallerid',
        'preprocess_subroutine',
        'mobilephonenumber',
        'bsfilter',
        'language',
    ]

    def __init__(self, **kwargs):
        for field_name in self._FIELDS:
            setattr(self, field_name, kwargs.get(field_name))

    @classmethod
    def from_data_source(cls, properties):
        return cls(**properties.__dict__)
