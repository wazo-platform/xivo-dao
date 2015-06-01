# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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


class Model(NewModel):

    _RELATION = {}


class FuncKeyTemplate(Model):

    FIELDS = ['id',
              'name',
              'description',
              'keys']

    MANDATORY = ['name']

    def __init__(self, **parameters):
        parameters.setdefault('keys', {})
        super(FuncKeyTemplate, self).__init__(**parameters)


class FuncKey(Model):

    FIELDS = ['id',
              'destination',
              'label',
              'blf']

    MANDATORY = ['position',
                 'destination']

    def __init__(self, **parameters):
        parameters.setdefault('blf', False)
        super(FuncKey, self).__init__(**parameters)


class UserDestination(Model):

    FIELDS = ['user_id']

    MANDATORY = ['user_id']


class GroupDestination(Model):

    FIELDS = ['group_id']

    MANDATORY = ['group_id']


class QueueDestination(Model):

    FIELDS = ['queue_id']

    MANDATORY = ['queue_id']


class ConferenceDestination(Model):

    FIELDS = ['conference_id']

    MANDATORY = ['conference_id']


class PagingDestination(Model):

    FIELDS = ['paging_id']

    MANDATORY = ['paging_id']


class BSFilterDestination(Model):

    FIELDS = ['filter_member_id']

    MANDATORY = ['filter_member_id']


class CustomDestination(Model):

    FIELDS = ['exten']

    MANDATORY = ['exten']


class ServiceDestination(Model):

    FIELDS = ['service']

    MANDATORY = ['service']


class ForwardDestination(Model):

    FIELDS = ['forward', 'exten']

    MANDATORY = ['forward', 'exten']


class TransferDestination(Model):

    FIELDS = ['transfer', 'exten']

    MANDATORY = ['forward', 'exten']


class AgentDestination(Model):

    FIELDS = ['action', 'agent_id']

    MANDATORY = ['action', 'agent_id']


class ParkPositionDestination(Model):

    FIELDS = ['position']

    MANDATORY = ['position']


class ParkingDestination(Model):

    FIELDS = []

    MANDATORY = []


class UserFuncKey(Model):

    MANDATORY = [
        'id',
        'user_id'
    ]

    FIELDS = [
        'id',
        'user_id'
    ]


class BSFilterFuncKey(Model):

    MANDATORY = [
        'id',
        'filter_id',
        'secretary_id',
    ]

    FIELDS = [
        'id',
        'filter_id',
        'secretary_id',
    ]


class ForwardTypeConverter(object):

    fwd_types = {
        'unconditional': 'fwdunc',
        'noanswer': 'fwdrna',
        'busy': 'fwdbusy',
    }

    reversed_types = dict((value, key) for key, value in fwd_types.iteritems())

    def db_to_model(self, db_type):
        return self.reversed_types[db_type]

    def model_to_db(self, model_type):
        return self.fwd_types[model_type]


Hint = namedtuple('Hint', ['user_id', 'extension', 'argument'])
Forward = namedtuple('Forward', ['user_id', 'type', 'number'])
