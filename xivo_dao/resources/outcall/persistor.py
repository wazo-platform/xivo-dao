# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.rightcallmember import RightCallMember

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class OutcallPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Outcall

    def __init__(self, session, outcall_search, tenant_uuids=None):
        self.session = session
        self.search_system = outcall_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Outcall)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def delete(self, outcall):
        self._delete_associations(outcall)
        self.session.delete(outcall)
        self.session.flush()

    def _delete_associations(self, outcall):
        (self.session.query(RightCallMember)
         .filter(RightCallMember.type == 'outcall')
         .filter(RightCallMember.typeval == str(outcall.id))
         .delete())

        for extension in outcall.extensions:
            extension.type = 'user'
            extension.typeval = '0'

    def associate_call_permission(self, outcall, call_permission):
        if call_permission not in outcall.call_permissions:
            outcall.call_permissions.append(call_permission)
            self.session.flush()
            self.session.expire(outcall, ['rightcall_members'])

    def dissociate_call_permission(self, outcall, call_permission):
        if call_permission in outcall.call_permissions:
            outcall.call_permissions.remove(call_permission)
            self.session.flush()
            self.session.expire(outcall, ['rightcall_members'])
