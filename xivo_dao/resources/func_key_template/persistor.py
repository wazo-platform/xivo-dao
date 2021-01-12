# -*- coding: utf-8 -*-
# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import abc
import six

from sqlalchemy import text

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_features import (
    FuncKeyDestFeatures,
    FuncKeyDestOnlineRecording,
    FuncKeyDestParking,
    FuncKeyDestTransfer,
)
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_group_member import FuncKeyDestGroupMember
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.func_key_dest_park_position import FuncKeyDestParkPosition
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser

from xivo_dao.helpers import errors

from xivo_dao.resources.extension.database import (
    ForwardExtensionConverter,
    AgentActionExtensionConverter,
    GroupMemberActionExtensionConverter,
)
from xivo_dao.resources.utils.search import SearchResult

from .search import template_search


def build_persistor(session, tenant_uuids=None):
    destination_persistors = {
        'agent': AgentPersistor,
        'bsfilter': BSFilterPersistor,
        'conference': ConferencePersistor,
        'custom': CustomPersistor,
        'features': FeaturesPersistor,
        'forward': ForwardPersistor,
        'group': GroupPersistor,
        'groupmember': GroupMemberPersistor,
        'onlinerec': FeaturesPersistor,
        'paging': PagingPersistor,
        'park_position': ParkPositionPersistor,
        'parking': FeaturesPersistor,
        'queue': QueuePersistor,
        'service': ServicePersistor,
        'transfer': FeaturesPersistor,
        'user': UserPersistor,
    }

    return FuncKeyPersistor(
        session,
        destination_persistors,
        template_search,
        tenant_uuids=tenant_uuids,
    )


class FuncKeyPersistor(object):

    def __init__(self, session, persistors, template_search, tenant_uuids=None):
        self.persistors = persistors
        self.session = session
        self.template_search = template_search
        self.tenant_uuids = tenant_uuids

    def search(self, parameters):
        query = self.session.query(FuncKeyTemplate.id)
        query = self._filter_tenant_uuid(query)
        rows, total = self.template_search.search_from_query(query, parameters)

        items = [self.get(row.id) for row in rows]
        return SearchResult(total=total, items=items)

    def create(self, template):
        template = self.add_template(template)
        funckeys = self.add_funckeys(template.id, template.keys)
        template.keys = funckeys
        return template

    def add_template(self, template):
        self.session.add(template)
        self.session.flush()
        return template

    def add_funckeys(self, template_id, funckeys):
        created_funckeys = {}
        for pos, funckey in six.iteritems(funckeys):
            created_funckeys[pos] = self.add_mapping(template_id, pos, funckey)
        return created_funckeys

    def add_mapping(self, template_id, position, funckey):
        destination_row = self.find_or_create_destination(funckey.destination)
        mapping = FuncKeyMapping(template_id=template_id,
                                 func_key_id=destination_row.func_key_id,
                                 destination_type_id=destination_row.destination_type_id,
                                 position=position,
                                 label=funckey.label,
                                 blf=funckey.blf)

        self.session.add(mapping)
        self.session.flush()
        mapping.destination = funckey.destination
        return mapping

    def find_or_create_destination(self, destination):
        persistor = self.build_persistor(destination.type)
        destination_row = persistor.find_or_create(destination)

        if not destination_row:
            raise errors.param_not_found('destination',
                                         'func key representing destination',
                                         type=destination.type)
        return destination_row

    def build_persistor(self, dest_type):
        persistor_cls = self.persistors[dest_type]
        return persistor_cls(self.session)

    def get(self, template_id):
        template = self.get_template_row(template_id)
        template.keys = self.get_keys_for_template(template_id)
        return template

    def get_template_row(self, template_id):
        query = self.session.query(FuncKeyTemplate)
        query = query.filter(FuncKeyTemplate.id == template_id)
        query = self._filter_tenant_uuid(query)
        template = query.first()
        if not template:
            raise errors.not_found('FuncKeyTemplate', id=template_id)
        return template

    def get_keys_for_template(self, template_id):
        keys = {}
        for row in self.query_mappings(template_id):
            row.destination = self.build_destination(row.func_key_id, row.destination_type_name)
            keys[row.position] = row
        return keys

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(FuncKeyTemplate.tenant_uuid.in_(self.tenant_uuids))

    def query_mappings(self, template_id):
        query = (self.session.query(FuncKeyMapping)
                 .filter(FuncKeyMapping.template_id == template_id))

        return query.all()

    def build_destination(self, func_key_id, dest_type):
        persistor = self.build_persistor(dest_type)
        return persistor.get(func_key_id)

    def delete(self, template):
        self.remove_funckeys(template)
        self.delete_template(template)
        self.session.flush()

    def remove_funckeys(self, template):
        for row in self.query_mappings(template.id):
            self.delete_mapping(row)
            self.delete_destination(row)

    def delete_mapping(self, mapping_row):
        (self.session.query(FuncKeyMapping)
         .filter(FuncKeyMapping.template_id == mapping_row.template_id)
         .filter(FuncKeyMapping.func_key_id == mapping_row.func_key_id)
         .filter(FuncKeyMapping.position == mapping_row.position)
         .delete())

    def delete_destination(self, row):
        persistor = self.build_persistor(row.destination_type_name)
        persistor.delete(row.func_key_id)

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


@six.add_metaclass(abc.ABCMeta)
class DestinationPersistor(object):

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

    def _func_key_is_still_mapped(self, func_key_id):
        return (self.session.query(FuncKeyMapping)
                .filter(FuncKeyMapping.func_key_id == func_key_id)
                .first())


class UserPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 1

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestUser)
                 .filter(FuncKeyDestUser.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        destination_row = (self.session.query(FuncKeyDestUser)
                           .filter(FuncKeyDestUser.user_id == destination.user_id)
                           .first())

        if not destination_row:
            func_key_row = self.create_func_key(self.TYPE_ID, self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestUser(func_key_id=func_key_row.id, user_id=destination.user_id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestUser)
             .filter(FuncKeyDestUser.func_key_id == func_key_id)
             .delete())


class QueuePersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 3

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestQueue)
                 .filter(FuncKeyDestQueue.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        destination_row = (self.session.query(FuncKeyDestQueue)
                           .filter(FuncKeyDestQueue.queue_id == destination.queue_id)
                           .first())

        if not destination_row:
            func_key_row = self.create_func_key(self.TYPE_ID, self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestQueue(func_key_id=func_key_row.id, queue_id=destination.queue_id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestQueue)
             .filter(FuncKeyDestQueue.func_key_id == func_key_id)
             .delete())


class GroupPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 2

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestGroup)
                 .filter(FuncKeyDestGroup.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        destination_row = (self.session.query(FuncKeyDestGroup)
                           .filter(FuncKeyDestGroup.group_id == destination.group_id)
                           .first())

        if not destination_row:
            func_key_row = self.create_func_key(self.TYPE_ID,
                                                self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestGroup(func_key_id=func_key_row.id,
                                               group_id=destination.group_id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestGroup)
             .filter(FuncKeyDestGroup.func_key_id == func_key_id)
             .delete())


class GroupMemberPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 13

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestGroupMember)
                 .filter(FuncKeyDestGroupMember.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        typeval = self.find_typeval(destination.action)

        destination_row = (self.session.query(FuncKeyDestGroupMember)
                           .join(Extension, FuncKeyDestGroupMember.extension_id == Extension.id)
                           .filter(FuncKeyDestGroupMember.group_id == destination.group_id)
                           .filter(Extension.type == 'extenfeatures')
                           .filter(Extension.typeval == typeval)
                           .first())
        if not destination_row:
            extension = (self.session.query(Extension)
                         .filter(Extension.type == 'extenfeatures')
                         .filter(Extension.typeval == typeval)
                         .first())

            func_key_row = self.create_func_key(self.TYPE_ID, self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestGroupMember(func_key_id=func_key_row.id,
                                                     group_id=destination.group_id,
                                                     extension_id=extension.id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def find_typeval(self, action):
        return GroupMemberActionExtensionConverter().to_typeval(action)

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestGroupMember)
             .filter(FuncKeyDestGroupMember.func_key_id == func_key_id)
             .delete())


class ConferencePersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 4

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestConference)
                 .filter(FuncKeyDestConference.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        destination_row = (self.session.query(FuncKeyDestConference)
                           .filter(FuncKeyDestConference.conference_id == destination.conference_id)
                           .first())

        if not destination_row:
            func_key_row = self.create_func_key(self.TYPE_ID,
                                                self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestConference(func_key_id=func_key_row.id,
                                                    conference_id=destination.conference_id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestConference)
             .filter(FuncKeyDestConference.func_key_id == func_key_id)
             .delete())


class PagingPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 9

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestPaging)
                 .filter(FuncKeyDestPaging.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        destination_row = (self.session.query(FuncKeyDestPaging)
                           .filter(FuncKeyDestPaging.paging_id == destination.paging_id)
                           .first())

        if not destination_row:
            func_key_row = self.create_func_key(self.TYPE_ID,
                                                self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestPaging(func_key_id=func_key_row.id,
                                                paging_id=destination.paging_id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestPaging)
             .filter(FuncKeyDestPaging.func_key_id == func_key_id)
             .delete())


class BSFilterPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 12

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestBSFilter)
                 .filter(FuncKeyDestBSFilter.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        destination_row = (self.session.query(FuncKeyDestBSFilter)
                           .filter(FuncKeyDestBSFilter.filtermember_id == destination.filter_member_id)
                           .first())

        if not destination_row:
            func_key_row = self.create_func_key(self.TYPE_ID,
                                                self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestBSFilter(func_key_id=func_key_row.id,
                                                  filter_member_id=destination.filter_member_id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestBSFilter)
             .filter(FuncKeyDestBSFilter.func_key_id == func_key_id)
             .delete())


class ServicePersistor(DestinationPersistor):

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestService)
                 .filter(FuncKeyDestService.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestService)
                 .join(Extension, FuncKeyDestService.extension_id == Extension.id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.typeval == destination.service))
        # NOTE(fblackburn): Already created by populate.sql

        return query.first()

    def delete(self, func_key_id):
        pass


class ForwardPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 6

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestForward)
                 .filter(FuncKeyDestForward.func_key_id == func_key_id))

        return query.first()

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
                 .filter(Extension.typeval == typeval))

        return query.scalar()

    def delete(self, func_key_id):
        (self.session.query(FuncKeyDestForward)
         .filter(FuncKeyDestForward.func_key_id == func_key_id)
         .delete())


class ParkPositionPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 7

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestParkPosition)
                 .filter(FuncKeyDestParkPosition.func_key_id == func_key_id))

        return query.first()

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


class CustomPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 10

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestCustom)
                 .filter(FuncKeyDestCustom.func_key_id == func_key_id))

        return query.first()

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


class AgentPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 11

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestAgent)
                 .filter(FuncKeyDestAgent.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        typeval = self.find_typeval(destination.action)

        destination_row = (self.session.query(FuncKeyDestAgent)
                           .join(Extension, FuncKeyDestAgent.extension_id == Extension.id)
                           .filter(FuncKeyDestAgent.agent_id == destination.agent_id)
                           .filter(Extension.type == 'extenfeatures')
                           .filter(Extension.typeval == typeval)
                           .first())
        if not destination_row:
            extension = (self.session.query(Extension)
                         .filter(Extension.type == 'extenfeatures')
                         .filter(Extension.typeval == typeval)
                         .first())

            func_key_row = self.create_func_key(self.TYPE_ID, self.DESTINATION_TYPE_ID)
            destination_row = FuncKeyDestAgent(func_key_id=func_key_row.id,
                                               agent_id=destination.agent_id,
                                               extension_id=extension.id)
            self.session.add(destination_row)
            self.session.flush()

        return destination_row

    def find_typeval(self, action):
        return AgentActionExtensionConverter().to_typeval(action)

    def delete(self, func_key_id):
        if not self._func_key_is_still_mapped(func_key_id):
            (self.session.query(FuncKeyDestAgent)
             .filter(FuncKeyDestAgent.func_key_id == func_key_id)
             .delete())


class FeaturesPersistor(DestinationPersistor):

    TRANSFERS_TO_API = {'blindxfer': 'blind',
                        'atxfer': 'attended'}

    TRANSFERS_TO_DB = {'blind': 'blindxfer',
                       'attended': 'atxfer'}

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestFeatures,
                                    Features.var_name,
                                    Features.id)
                 .join(Features, FuncKeyDestFeatures.features_id == Features.id)
                 .filter(FuncKeyDestFeatures.func_key_id == func_key_id))

        result = query.first()

        if result.var_name == 'parkext':
            return FuncKeyDestParking(feature_id=result.id)
        elif result.var_name == 'togglerecord':
            return FuncKeyDestOnlineRecording(feature_id=result.id)

        transfer = self.TRANSFERS_TO_API[result.var_name]
        return FuncKeyDestTransfer(feature_id=result.id, transfer=transfer)

    def find_or_create(self, destination):
        varname = self.find_var_name(destination)

        query = (self.session.query(FuncKeyDestFeatures)
                 .join(Features, FuncKeyDestFeatures.features_id == Features.id)
                 .filter(Features.var_name == varname))
        # NOTE(fblackburn): Already created by populate.sql

        return query.first()

    def find_var_name(self, destination):
        if destination.type == 'transfer':
            return self.TRANSFERS_TO_DB[destination.transfer]
        elif destination.type == 'parking':
            return 'parkext'
        elif destination.type == 'onlinerec':
            return 'togglerecord'

    def delete(self, func_key_id):
        pass
