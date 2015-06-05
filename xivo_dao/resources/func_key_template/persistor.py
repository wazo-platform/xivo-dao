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
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType
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

from xivo_dao.helpers import errors
from xivo_dao.resources.func_key import model as m

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
                              'features': FeaturesPersistor,
                              }
    return FuncKeyPersistor(session, destination_persistors)


class FuncKeyPersistor(object):

    def __init__(self, session, persistors):
        self.persistors = persistors
        self.session = session

    def create(self, template):
        template_id = self.add_template(template)
        self.add_funckeys(template_id, template.keys)
        template.id = template_id
        return template

    def add_template(self, template):
        row = FuncKeyTemplate(name=template.name)
        self.session.add(row)
        self.session.flush()
        return row.id

    def add_funckeys(self, template_id, funckeys):
        for pos, funckey in funckeys.iteritems():
            self.add_mapping(template_id, pos, funckey)

    def add_mapping(self, template_id, position, funckey):
        destination_row = self.find_or_create_destination(funckey.destination)
        mapping = FuncKeyMapping(template_id=template_id,
                                 func_key_id=destination_row.func_key_id,
                                 destination_type_id=destination_row.destination_type_id,
                                 position=position,
                                 label=funckey.label,
                                 blf=funckey.blf)

        self.session.add(mapping)
        funckey.id = destination_row.func_key_id

    def find_or_create_destination(self, destination):
        persistor = self.build_persistor(destination.type)
        return persistor.find_or_create(destination)

    def build_persistor(self, dest_type):
        persistor_cls = self.persistors[dest_type]
        return persistor_cls(self.session)

    def get(self, template_id):
        template = self.get_template(template_id)
        template.keys = self.get_keys_for_template(template_id)
        return template

    def get_template(self, template_id):
        template_row = self.get_template_row(template_id)
        return m.FuncKeyTemplate(id=template_row.id,
                                 name=template_row.name)

    def get_template_row(self, template_id):
        template_row = self.session.query(FuncKeyTemplate).get(template_id)
        if not template_row:
            raise errors.not_found('FuncKeyTemplate', id=template_id)
        return template_row

    def get_keys_for_template(self, template_id):
        return {mapping_row.position: self.build_func_key(mapping_row, dest_type)
                for mapping_row, dest_type in self.query_mappings(template_id)}

    def build_func_key(self, mapping_row, dest_type):
        return m.FuncKey(id=mapping_row.func_key_id,
                         label=mapping_row.label,
                         blf=mapping_row.blf,
                         destination=self.build_destination(mapping_row, dest_type))

    def query_mappings(self, template_id):
        query = (self.session.query(FuncKeyMapping,
                                    FuncKeyDestinationType.name)
                 .join(FuncKeyDestinationType, FuncKeyMapping.destination_type_id == FuncKeyDestinationType.id)
                 .filter(FuncKeyMapping.template_id == template_id)
                 )

        return query

    def build_destination(self, mapping_row, dest_type):
        persistor = self.build_persistor(dest_type)
        return persistor.get(mapping_row.func_key_id)

    def delete(self, template):
        self.remove_funckeys(template)
        self.delete_template(template)

    def remove_funckeys(self, template):
        for mapping_row, dest_type in self.query_mappings(template.id):
            self.delete_mapping(mapping_row)
            self.delete_destination(mapping_row, dest_type)

    def delete_mapping(self, mapping_row):
        (self.session.query(FuncKeyMapping)
         .filter(FuncKeyMapping.template_id == mapping_row.template_id)
         .filter(FuncKeyMapping.func_key_id == mapping_row.func_key_id)
         .filter(FuncKeyMapping.position == mapping_row.position)
         .delete())

    def delete_destination(self, mapping_row, dest_type):
        persistor = self.build_persistor(dest_type)
        persistor.delete(mapping_row.func_key_id)

    def delete_template(self, template):
        (self.session.query(FuncKeyTemplate)
         .filter(FuncKeyTemplate.id == template.id)
         .delete())

    def edit(self, template):
        self.update_template(template)
        self.update_funckeys(template)

    def update_template(self, template):
        template_row = self.get_template_row(template.id)
        template_row.name = template.name
        self.session.add(template_row)

    def update_funckeys(self, template):
        self.remove_funckeys(template)
        self.add_funckeys(template.id, template.keys)


class DestinationPersistor(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, session):
        self.session = session

    @abc.abstractmethod
    def get(self, func_key_id):
        return

    @abc.abstractmethod
    def find_or_create(self, destination):
        return

    @abc.abstractmethod
    def delete(self, func_key_id):
        return

    def create_func_key(self, type_id, destination_type_id):
        func_key_row = FuncKey(type_id=type_id,
                               destination_type_id=destination_type_id)
        self.session.add(func_key_row)
        self.session.flush()
        return func_key_row

    def delete_func_key(self, func_key_id):
        (self.session.query(FuncKey)
         .filter(FuncKey.id == func_key_id)
         .delete())


class UserPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestUser.user_id)
               .filter(FuncKeyDestUser.func_key_id == func_key_id)
               .first())

        return m.UserDestination(user_id=row.user_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestUser)
                 .filter(FuncKeyDestUser.user_id == destination.user_id)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class QueuePersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestQueue.queue_id)
               .filter(FuncKeyDestQueue.func_key_id == func_key_id)
               .first())

        return m.QueueDestination(queue_id=row.queue_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestQueue)
                 .filter(FuncKeyDestQueue.queue_id == destination.queue_id)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class GroupPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestGroup.group_id)
               .filter(FuncKeyDestGroup.func_key_id == func_key_id)
               .first())

        return m.GroupDestination(group_id=row.group_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestGroup)
                 .filter(FuncKeyDestGroup.group_id == destination.group_id)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class ConferencePersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestConference.conference_id)
               .filter(FuncKeyDestConference.func_key_id == func_key_id)
               .first())

        return m.ConferenceDestination(conference_id=row.conference_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestConference)
                 .filter(FuncKeyDestConference.conference_id == destination.conference_id)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class PagingPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestPaging.paging_id)
               .filter(FuncKeyDestPaging.func_key_id == func_key_id)
               .first())

        return m.PagingDestination(paging_id=row.paging_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestPaging)
                 .filter(FuncKeyDestPaging.paging_id == destination.paging_id)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class BSFilterPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestBSFilter.filtermember_id)
               .filter(FuncKeyDestBSFilter.func_key_id == func_key_id)
               .first())

        return m.BSFilterDestination(filter_member_id=row.filtermember_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestBSFilter)
                 .filter(FuncKeyDestBSFilter.filtermember_id == destination.filter_member_id)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class ServicePersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(Extension.typeval)
               .join(FuncKeyDestService, FuncKeyDestService.extension_id == Extension.id)
               .filter(FuncKeyDestService.func_key_id == func_key_id)
               .first())

        return m.ServiceDestination(service=row.typeval)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestService)
                 .join(Extension, FuncKeyDestService.extension_id == Extension.id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.commented == 0)
                 .filter(Extension.typeval == destination.service)
                 )

        return query.first()

    def delete(self, func_key_id):
        pass


class ForwardPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 6

    def get(self, func_key_id):
        row = (self.session.query(Extension.typeval,
                                  FuncKeyDestForward.number)
               .join(FuncKeyDestForward, FuncKeyDestForward.extension_id == Extension.id)
               .filter(FuncKeyDestForward.func_key_id == func_key_id)
               .first())

        forward = ForwardExtensionConverter().to_forward(row.typeval)

        return m.ForwardDestination(forward=forward,
                                    exten=row.number)

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

    def delete(self, func_key_id):
        (self.session.query(FuncKeyDestForward)
         .filter(FuncKeyDestForward.func_key_id == func_key_id)
         .delete())
        self.delete_func_key(func_key_id)


class ParkPositionPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 7

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestParkPosition.park_position)
               .filter(FuncKeyDestParkPosition.func_key_id == func_key_id)
               .first())

        return m.ParkPositionDestination(position=int(row.park_position))

    def find_or_create(self, destination):
        func_key_row = self.create_func_key(self.TYPE_ID,
                                            self.DESTINATION_TYPE_ID)

        destination_row = FuncKeyDestParkPosition(func_key_id=func_key_row.id,
                                                  park_position=str(destination.position))

        self.session.add(destination_row)
        self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        (self.session.query(FuncKeyDestParkPosition)
         .filter(FuncKeyDestParkPosition.func_key_id == func_key_id)
         .delete())
        self.delete_func_key(func_key_id)


class CustomPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 10

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestCustom.exten)
               .filter(FuncKeyDestCustom.func_key_id == func_key_id)
               .first())

        return m.CustomDestination(exten=row.exten)

    def find_or_create(self, destination):
        func_key_row = self.create_func_key(self.TYPE_ID,
                                            self.DESTINATION_TYPE_ID)

        destination_row = FuncKeyDestCustom(func_key_id=func_key_row.id,
                                            exten=destination.exten)

        self.session.add(destination_row)
        self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        (self.session.query(FuncKeyDestCustom)
         .filter(FuncKeyDestCustom.func_key_id == func_key_id)
         .delete())
        self.delete_func_key(func_key_id)


class AgentPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestAgent.agent_id,
                                  Extension.typeval)
               .join(Extension, FuncKeyDestAgent.extension_id == Extension.id)
               .filter(FuncKeyDestAgent.func_key_id == func_key_id)
               .first()
               )

        action = AgentActionExtensionConverter().to_action(row.typeval)

        return m.AgentDestination(action=action,
                                  agent_id=row.agent_id)

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

    def delete(self, func_key_id):
        pass


class FeaturesPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(Features.var_name)
               .join(FuncKeyDestFeatures, FuncKeyDestFeatures.features_id == Features.id)
               .filter(FuncKeyDestFeatures.func_key_id == func_key_id)
               .first()
               )

        if row.var_name == 'parkext':
            return m.ParkingDestination()

        transfer = TransferExtensionConverter().to_transfer(row.var_name)
        return m.TransferDestination(transfer=transfer)

    def find_or_create(self, destination):
        varname = self.find_var_name(destination)

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

    def delete(self, func_key_id):
        pass
