# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class CustomPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Custom

    def __init__(self, session, custom_search, tenant_uuids=None):
        self.session = session
        self.search_system = custom_search
        self.tenant_uuids = tenant_uuids

    def get(self, custom_id):
        custom = self._find_query({'id': custom_id}).first()
        if not custom:
            raise errors.not_found('CustomEndpoint', id=id)
        return custom

    def _find_query(self, criteria):
        query = self.session.query(Custom)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def create(self, custom):
        self.fill_default_values(custom)
        self.session.add(custom)
        self.session.flush()
        return custom

    def fill_default_values(self, custom):
        if custom.protocol is None:
            custom.protocol = 'custom'
        if custom.category is None:
            custom.category = 'user'

    def edit(self, custom):
        self.session.add(custom)
        self.session.flush()
        self._fix_associated(custom)

    def delete(self, custom):
        self.session.query(Custom).filter_by(id=custom.id).delete()
        self.session.expire_all()
        self.session.flush()
        self._fix_associated(custom)

    def _fix_associated(self, custom):
        if custom.line:
            LineFixes(self.session).fix(custom.line.id)

        if custom.trunk:
            TrunkFixes(self.session).fix(custom.trunk.id)
