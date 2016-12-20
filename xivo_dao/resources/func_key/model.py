# -*- coding: utf-8 -*-

# Copyright 2014-2016 The Wazo Authors  (see the AUTHORS file)
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

import abc

from collections import namedtuple

from xivo_dao.helpers.new_model import NewModel


class Model(NewModel):

    _RELATION = {}


class FuncKey(Model):

    FIELDS = ['id',
              'destination',
              'label',
              'blf',
              'inherited']

    MANDATORY = ['position',
                 'destination']

    def __init__(self, **parameters):
        parameters.setdefault('blf', True)
        parameters.setdefault('inherited', True)
        super(FuncKey, self).__init__(**parameters)

    def hash_destination(self):
        return self.destination.to_tuple()


class Destination(Model):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def type(self):
        return

    def to_tuple(self):
        parameters = ((key, getattr(self, key)) for key in self.FIELDS)
        return tuple(sorted(parameters))


class UserDestination(Destination):

    type = 'user'

    FIELDS = ['user_id']

    MANDATORY = ['user_id']

    _RELATION = {'userfeatures': 'userfeatures'}


class GroupDestination(Destination):

    type = 'group'

    FIELDS = ['group_id']

    MANDATORY = ['group_id']


class QueueDestination(Destination):

    type = 'queue'

    FIELDS = ['queue_id']

    MANDATORY = ['queue_id']


class ConferenceDestination(Destination):

    type = 'conference'

    FIELDS = ['conference_id']

    MANDATORY = ['conference_id']


class PagingDestination(Destination):

    type = 'paging'

    FIELDS = ['paging_id']

    MANDATORY = ['paging_id']


class BSFilterDestination(Destination):

    type = 'bsfilter'

    FIELDS = ['filter_member_id']

    MANDATORY = ['filter_member_id']


class CustomDestination(Destination):

    type = 'custom'

    FIELDS = ['exten']

    MANDATORY = ['exten']


class ServiceDestination(Destination):

    type = 'service'

    FIELDS = ['service',
              'extension_id']

    MANDATORY = ['service']

    def to_tuple(self):
        return (('service', self.service),)


class ForwardDestination(Destination):

    type = 'forward'

    FIELDS = ['forward',
              'exten',
              'extension_id']

    MANDATORY = ['forward']

    def to_tuple(self):
        return (('exten', self.exten), ('forward', self.forward))


class TransferDestination(Destination):

    type = 'transfer'

    FIELDS = ['transfer',
              'feature_id']

    MANDATORY = ['transfer']

    def to_tuple(self):
        return (('transfer', self.transfer),)


class AgentDestination(Destination):

    type = 'agent'

    FIELDS = ['action', 'agent_id', 'extension_id']

    MANDATORY = ['action', 'agent_id']

    def to_tuple(self):
        return (('action', self.action), ('agent_id', self.agent_id))


class ParkPositionDestination(Destination):

    type = 'park_position'

    FIELDS = ['position']

    MANDATORY = ['position']


class ParkingDestination(Destination):

    type = 'parking'

    FIELDS = ['feature_id']

    MANDATORY = []

    def to_tuple(self):
        return (('feature', 'parking'),)


class OnlineRecordingDestination(Destination):

    type = 'onlinerec'

    FIELDS = ['feature_id']

    MANDATORY = []

    def to_tuple(self):
        return (('feature', 'onlinerec'),)


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
