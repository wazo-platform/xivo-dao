# -*- coding: utf-8 -*-
# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers import errors, generators
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class SipPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = EndpointSIP

    def __init__(self, session, sip_search, tenant_uuids=None):
        self.session = session
        self.search_system = sip_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(EndpointSIP)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        sip = self.find_by(criteria)
        if not sip:
            template = criteria.pop('template', None)
            if template:
                raise errors.not_found('SIPEndpointTemplate', **criteria)
            else:
                raise errors.not_found('SIPEndpoint', **criteria)
        return sip

    def _search_query(self):
        return (
            self.session
            .query(self.search_system.config.table)
            .options(joinedload('transport'))
            .options(joinedload('template_relations').joinedload('parent'))
            .options(joinedload('_aor_section'))
            .options(joinedload('_auth_section'))
            .options(joinedload('_endpoint_section'))
            .options(joinedload('_registration_section'))
            .options(joinedload('_registration_outbound_auth_section'))
            .options(joinedload('_identify_section'))
            .options(joinedload('_outbound_auth_section'))
            .options(joinedload('line'))
            .options(joinedload('trunk'))
        )

    def create(self, sip):
        self._fill_default_values(sip)
        self.session.add(sip)
        self.session.flush()
        return sip

    def edit(self, sip):
        self.persist(sip)
        self._fix_associated(sip)

    def delete(self, sip):
        self.session.delete(sip)
        self._fix_associated(sip)

    def _fix_associated(self, sip):
        if sip.line:
            LineFixes(self.session).fix(sip.line.id)

        if sip.trunk:
            TrunkFixes(self.session).fix(sip.trunk.id)

    def _fill_default_values(self, sip):
        if sip.name is None:
            sip.name = generators.find_unused_hash(self._name_already_exists)

    def _name_already_exists(self, data):
        return self.session.query(EndpointSIP).filter(EndpointSIP.name == data).count() > 0
