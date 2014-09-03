# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from collections import namedtuple


from xivo_dao.helpers.new_model import NewModel


class FuncKey(NewModel):

    MANDATORY = [
        'type',
        'destination',
        'destination_id',
    ]

    FIELDS = [
        'id',
        'type',
        'destination',
        'destination_id',
    ]

    _RELATION = {}


class ForwardTypeConverter(object):

    fwd_types = {
        'unconditional': 'fwdunc',
        'noanswer': 'fwdrna',
        'busy': 'fwdbusy',
    }

    reveresed_types = dict((value, key) for key, value in fwd_types.iteritems())

    def db_to_model(self, db_type):
        return self.reveresed_types[db_type]

    def model_to_db(self, model_type):
        return self.fwd_types[model_type]


Hint = namedtuple('Hint', ['user_id', 'exten', 'type', 'number'])
Forward = namedtuple('Forward', ['user_id', 'type', 'number'])

