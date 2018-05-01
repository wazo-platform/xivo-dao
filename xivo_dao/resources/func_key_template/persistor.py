# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import abc
import six
from sqlalchemy import sql

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
from xivo_dao.resources.func_key import model as fk_model

from xivo_dao.resources.extension.database import ForwardExtensionConverter, AgentActionExtensionConverter


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
                              'onlinerec': FeaturesPersistor}
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
        self.session.add(template)
        self.session.flush()
        return template.id

    def add_funckeys(self, template_id, funckeys):
        for pos, funckey in six.iteritems(funckeys):
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
        template_row = self.session.query(FuncKeyTemplate).get(template_id)
        if not template_row:
            raise errors.not_found('FuncKeyTemplate', id=template_id)
        return template_row

    def get_keys_for_template(self, template_id):
        return {row.position: self.build_func_key(row)
                for row in self.query_mappings(template_id)}

    def build_func_key(self, mapping_row):
        return FuncKeyMapping(
            template_id=mapping_row.template_id,
            func_key_id=mapping_row.func_key_id,
            position=mapping_row.position,
            label=mapping_row.label,
            blf=mapping_row.blf,
            inherited=mapping_row.inherited,
            destination=self.build_destination(mapping_row),
        )

    def query_mappings(self, template_id):
        query = (self.session.query(FuncKeyMapping.template_id,
                                    FuncKeyMapping.func_key_id,
                                    FuncKeyMapping.position,
                                    FuncKeyMapping.label,
                                    FuncKeyMapping.blf,
                                    FuncKeyDestinationType.name.label('dest_type'),
                                    sql.not_(FuncKeyTemplate.private).label('inherited'))
                 .join(FuncKeyDestinationType, FuncKeyMapping.destination_type_id == FuncKeyDestinationType.id)
                 .join(FuncKeyTemplate, FuncKeyMapping.template_id == FuncKeyTemplate.id)
                 .filter(FuncKeyMapping.template_id == template_id))

        return query

    def build_destination(self, mapping_row):
        persistor = self.build_persistor(mapping_row.dest_type)
        return persistor.get(mapping_row.func_key_id)

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
        persistor = self.build_persistor(row.dest_type)
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

    def delete_func_key(self, func_key_id):
        (self.session.query(FuncKey)
         .filter(FuncKey.id == func_key_id)
         .delete())

    def _func_key_is_still_mapped(self, func_key_id):
        return (self.session.query(FuncKeyMapping)
                .filter(FuncKeyMapping.func_key_id == func_key_id)
                .first())


class UserPersistor(DestinationPersistor):

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestUser)
                 .filter(FuncKeyDestUser.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestUser)
                 .filter(FuncKeyDestUser.user_id == destination.user_id))

        return query.first()

    def delete(self, func_key_id):
        pass


class QueuePersistor(DestinationPersistor):

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestQueue)
                 .filter(FuncKeyDestQueue.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestQueue)
                 .filter(FuncKeyDestQueue.queue_id == destination.queue_id))

        return query.first()

    def delete(self, func_key_id):
        pass


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
            self.delete_func_key(func_key_id)


class ConferencePersistor(DestinationPersistor):

    def get(self, func_key_id):
        query = (self.session.query(FuncKeyDestConference)
                 .filter(FuncKeyDestConference.func_key_id == func_key_id))

        return query.first()

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestConference)
                 .filter(FuncKeyDestConference.conference_id == destination.conference_id))

        return query.first()

    def delete(self, func_key_id):
        pass


class PagingPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 9

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestPaging.paging_id)
               .filter(FuncKeyDestPaging.func_key_id == func_key_id)
               .first())

        return fk_model.PagingDestination(paging_id=row.paging_id)

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
            self.delete_func_key(func_key_id)


class BSFilterPersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestBSFilter.filtermember_id)
               .filter(FuncKeyDestBSFilter.func_key_id == func_key_id)
               .first())

        return fk_model.BSFilterDestination(filter_member_id=row.filtermember_id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestBSFilter)
                 .filter(FuncKeyDestBSFilter.filtermember_id == destination.filter_member_id))

        return query.first()

    def delete(self, func_key_id):
        pass


class ServicePersistor(DestinationPersistor):

    def get(self, func_key_id):
        row = (self.session.query(Extension.typeval,
                                  Extension.id)
               .join(FuncKeyDestService, FuncKeyDestService.extension_id == Extension.id)
               .filter(FuncKeyDestService.func_key_id == func_key_id)
               .first())

        return fk_model.ServiceDestination(service=row.typeval,
                                           extension_id=row.id)

    def find_or_create(self, destination):
        query = (self.session.query(FuncKeyDestService)
                 .join(Extension, FuncKeyDestService.extension_id == Extension.id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.typeval == destination.service))

        return query.first()

    def delete(self, func_key_id):
        pass


class ForwardPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 6

    def get(self, func_key_id):
        row = (self.session.query(Extension.typeval,
                                  Extension.id,
                                  FuncKeyDestForward.number)
               .join(FuncKeyDestForward, FuncKeyDestForward.extension_id == Extension.id)
               .filter(FuncKeyDestForward.func_key_id == func_key_id)
               .first())

        forward = ForwardExtensionConverter().to_forward(row.typeval)

        return fk_model.ForwardDestination(forward=forward,
                                           exten=row.number,
                                           extension_id=row.id)

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
        self.delete_func_key(func_key_id)


class ParkPositionPersistor(DestinationPersistor):

    TYPE_ID = 1
    DESTINATION_TYPE_ID = 7

    def get(self, func_key_id):
        row = (self.session.query(FuncKeyDestParkPosition.park_position)
               .filter(FuncKeyDestParkPosition.func_key_id == func_key_id)
               .first())

        return fk_model.ParkPositionDestination(position=int(row.park_position))

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

        return fk_model.CustomDestination(exten=row.exten)

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
                                  Extension.typeval,
                                  Extension.id)
               .join(Extension, FuncKeyDestAgent.extension_id == Extension.id)
               .filter(FuncKeyDestAgent.func_key_id == func_key_id)
               .first())

        action = AgentActionExtensionConverter().to_action(row.typeval)

        return fk_model.AgentDestination(action=action,
                                         agent_id=row.agent_id,
                                         extension_id=row.id)

    def find_or_create(self, destination):
        typeval = self.find_typeval(destination.action)

        query = (self.session.query(FuncKeyDestAgent)
                 .join(Extension, FuncKeyDestAgent.extension_id == Extension.id)
                 .filter(FuncKeyDestAgent.agent_id == destination.agent_id)
                 .filter(Extension.type == 'extenfeatures')
                 .filter(Extension.typeval == typeval))

        return query.first()

    def find_typeval(self, action):
        return AgentActionExtensionConverter().to_typeval(action)

    def delete(self, func_key_id):
        pass


class FeaturesPersistor(DestinationPersistor):

    TRANSFERS_TO_API = {'blindxfer': 'blind',
                        'atxfer': 'attended'}

    TRANSFERS_TO_DB = {'blind': 'blindxfer',
                       'attended': 'atxfer'}

    def get(self, func_key_id):
        row = (self.session.query(Features.var_name,
                                  Features.id)
               .join(FuncKeyDestFeatures, FuncKeyDestFeatures.features_id == Features.id)
               .filter(FuncKeyDestFeatures.func_key_id == func_key_id)
               .first())

        if row.var_name == 'parkext':
            return fk_model.ParkingDestination(feature_id=row.id)
        elif row.var_name == 'automixmon':
            return fk_model.OnlineRecordingDestination(feature_id=row.id)

        transfer = self.TRANSFERS_TO_API[row.var_name]
        return fk_model.TransferDestination(transfer=transfer,
                                            feature_id=row.id)

    def find_or_create(self, destination):
        varname = self.find_var_name(destination)

        query = (self.session.query(FuncKeyDestFeatures)
                 .join(Features, FuncKeyDestFeatures.features_id == Features.id)
                 .filter(Features.var_name == varname))

        return query.first()

    def find_var_name(self, destination):
        if destination.type == 'transfer':
            return self.TRANSFERS_TO_DB[destination.transfer]
        elif destination.type == 'parking':
            return 'parkext'
        elif destination.type == 'onlinerec':
            return 'automixmon'

    def delete(self, func_key_id):
        pass
