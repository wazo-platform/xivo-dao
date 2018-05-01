# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import abc
import six

from collections import namedtuple

from xivo_dao.helpers.new_model import NewModel


class Model(NewModel):

    _RELATION = {}


@six.add_metaclass(abc.ABCMeta)
class Destination(Model):

    @abc.abstractproperty
    def type(self):
        return

    def to_tuple(self):
        parameters = ((key, getattr(self, key)) for key in self.FIELDS)
        return tuple(sorted(parameters))


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


Hint = namedtuple('Hint', ['user_id', 'extension', 'argument'])
