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

import abc

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_features import FuncKeyDestFeatures
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_park_position import FuncKeyDestParkPosition

from xivo_dao.resources.extension.database import ForwardExtensionConverter, AgentActionExtensionConverter
from xivo_dao.resources.features.database import TransferExtensionConverter


def build_persistor(session):
    destination_persistors = {'user': UserPersistor,
                              'queue': QueuePersistor,
                              'group': GroupPersistor,
                              'conference': ConferencePersistor,
                              'paging': PagingPersistor,
                              'bsfilter': BSFilterPersistor,
                              'service': ServicePersistor,
                              'forward': ForwardPersistor,
                              'park_position': ParkPositionPersistor,
                              'custom': CustomPersistor,
                              'agent': AgentPersistor,
                              'transfer': FeaturesPersistor,
                              'parking': FeaturesPersistor,
                              }
    return FuncKeyPersistor(session, destination_persistors)


class FuncKeyPersistor(object):

    def __init__(self, session, persistors):
        self.persistors = persistors
        self.session = session

    def create(self, template):
        template_id = self.add_template(template)
        self.add_funckeys(template_id, template.keys)

    def add_template(self, template):
        row = FuncKeyTemplate(name=template.name)
        self.session.add(row)
        self.session.flush()
        return row.id

    def add_funckeys(self, template_id, funckeys):
        for pos, funckey in funckeys.iteritems():
            self.add_mapping(template_id, pos, funckey)

    def add_mapping(self, template_id, position, funckey):
        func_key_row = self.find_or_create_destination(funckey.destination)
        mapping = FuncKeyMapping(template_id=template_id,
                                 func_key_id=func_key_row.func_key_id,
                                 destination_type_id=func_key_row.destination_type_id,
                                 position=position,
                                 label=funckey.label,
                                 blf=funckey.blf)

        self.session.add(mapping)

    def find_or_create_destination(self, destination):
        persistor = self.build_persistor(destination.type)
        return persistor.find_or_create(destination)

    def build_persistor(self, dest_type):
        persistor_cls = self.persistors[dest_type]
        return persistor_cls(self.session)


class DestinationPersistor(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, session):
        self.session = session

    @abc.abstractmethod
    def find_or_create(self, destination):
        return

    def create_func_key(self, type_id, destination_type_id):
        func_key_row = FuncKey(type_id=type_id,
                               destination_type_id=destination_type_id)
        self.session.add(func_key_row)
        self.session.flush()
        return func_key_row


class UserPersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestUser)
                 .filter(FuncKeyDestUser.user_id == destination.user_id)
                 )

        return query.first()


class QueuePersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestQueue)
                 .filter(FuncKeyDestQueue.queue_id == destination.queue_id)
                 )

        return query.first()


class GroupPersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestGroup)
                 .filter(FuncKeyDestGroup.group_id == destination.group_id)
                 )

        return query.first()


class ConferencePersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestConference)
                 .filter(FuncKeyDestConference.conference_id == destination.conference_id)
                 )

        return query.first()


class PagingPersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestPaging)
                 .filter(FuncKeyDestPaging.paging_id == destination.paging_id)
                 )

        return query.first()


class BSFilterPersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestBSFilter)
                 .filter(FuncKeyDestBSFilter.filtermember_id == destination.filter_member_id)
                 )

        return query.first()


class ServicePersistor(DestinationPersistor):

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestService)
                 .join(Extension, FuncKeyDestService.extension_id == Extension.id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.commented == 0)
                 .filter(Extension.typeval == destination.service)
                 )

        return query.first()


class ForwardPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 6

    def find_or_create(self, destination):
        func_key_row = self.create_func_key(self.TYPE_ID,
                                            self.DESTINATION_TYPE_ID)
        extension_id = self.find_extension_id(destination.forward)

        destination_row = FuncKeyDestForward(func_key_id=func_key_row.id,
                                             extension_id=extension_id,
                                             number=destination.exten)
        self.session.add(destination_row)
        self.session.flush()

        return destination_row


    def find_extension_id(self, forward):
        typeval = ForwardExtensionConverter().to_typeval(forward)

        query = (self.session.query(Extension.id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.typeval == typeval)
                 .filter(Extension.commented == 0))

        return query.scalar()


class ParkPositionPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 7

    def find_or_create(self, destination):
        func_key_row = self.create_func_key(self.TYPE_ID,
                                            self.DESTINATION_TYPE_ID)

        destination_row = FuncKeyDestParkPosition(func_key_id=func_key_row.id,
                                                  park_position=str(destination.position))

        self.session.add(destination_row)
        self.session.flush()

        return destination_row


class CustomPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 10

    def find_or_create(self, destination):
        func_key_row = self.create_func_key(self.TYPE_ID,
                                            self.DESTINATION_TYPE_ID)

        destination_row = FuncKeyDestCustom(func_key_id=func_key_row.id,
                                            exten=destination.exten)

        self.session.add(destination_row)
        self.session.flush()

        return destination_row


class AgentPersistor(DestinationPersistor):

    def find_or_create(self, destination):
        typeval = self.find_typeval(destination.action)

        query = (self.session.query(FuncKeyDestAgent)
                 .join(Extension, FuncKeyDestAgent.extension_id == Extension.id)
                 .filter(FuncKeyDestAgent.agent_id == destination.agent_id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.typeval == typeval)
                 .filter(Extension.commented == 0)
                 )

        return query.first()

    def find_typeval(self, action):
        return AgentActionExtensionConverter().to_typeval(action)


class FeaturesPersistor(DestinationPersistor):




    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestFeatures)
                 .join(Features, FuncKeyDestFeatures.features_id == Features.id)
                 .filter(Features.var_name == varname)
                 .filter(Features.commented == 0)
                 )

        return query.first()

    def find_var_name(self, destination):
        if destination.type == 'transfer':
            return TransferExtensionConverter().to_var_name(destination.transfer)
        elif destination.type == 'parking':
            return 'parkext'
