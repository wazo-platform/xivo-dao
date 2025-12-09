# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.extension.search import extension_search
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class ExtensionPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = Extension

    def __init__(self, session, tenant_uuids=None):
        self.session = session
        self.tenant_uuids = tenant_uuids
        self.search_system = extension_search

    def _find_query(self, criteria):
        query = self.session.query(Extension)
        query = self.build_criteria(query, criteria)
        query = self._add_tenant_filter(query)
        return query

    def _search_query(self):
        return (
            self.session.query(Extension)
            .options(joinedload(Extension.conference))
            .options(joinedload(Extension.dialpattern).joinedload(DialPattern.outcall))
            .options(joinedload(Extension.group))
            .options(joinedload(Extension.context_rel))
            .options(joinedload(Extension.queue))
            .options(joinedload(Extension.incall))
            .options(
                joinedload(Extension.line_extensions).joinedload(LineExtension.line)
            )
            .options(joinedload(Extension.parking_lot))
        )

    def create(self, extension):
        self.fill_default_values(extension)
        self.session.add(extension)
        self.session.flush()
        return extension

    def fill_default_values(self, extension):
        if not extension.type:
            extension.type = 'user'
        if not extension.typeval:
            extension.typeval = '0'

    def delete(self, extension):
        self.session.query(Extension).filter(Extension.id == extension.id).delete()
        self.session.flush()

    def associate_incall(self, incall, extension):
        extension.type = 'incall'
        extension.typeval = str(incall.id)
        self.session.flush()
        self.session.expire(incall, ['extensions'])

    def dissociate_incall(self, incall, extension):
        if incall is extension.incall:
            extension.type = 'user'
            extension.typeval = '0'
            self.session.flush()
            self.session.expire(incall, ['extensions'])

    def associate_group(self, group, extension):
        extension.type = 'group'
        extension.typeval = str(group.id)
        self.session.flush()
        self.session.expire(group, ['extensions'])

    def dissociate_group(self, group, extension):
        if group is extension.group:
            extension.type = 'user'
            extension.typeval = '0'
            self.session.flush()
            self.session.expire(group, ['extensions'])

    def associate_queue(self, queue, extension):
        extension.type = 'queue'
        extension.typeval = str(queue.id)
        self.session.flush()
        self.session.expire(queue, ['extensions'])

    def dissociate_queue(self, queue, extension):
        if queue is extension.queue:
            extension.type = 'user'
            extension.typeval = '0'
            self.session.flush()
            self.session.expire(queue, ['extensions'])

    def associate_conference(self, conference, extension):
        extension.type = 'conference'
        extension.typeval = str(conference.id)
        self.session.flush()
        self.session.expire(conference, ['extensions'])

    def dissociate_conference(self, conference, extension):
        if conference is extension.conference:
            extension.type = 'user'
            extension.typeval = '0'
            self.session.flush()
            self.session.expire(conference, ['extensions'])

    def associate_parking_lot(self, parking_lot, extension):
        extension.type = 'parking'
        extension.typeval = str(parking_lot.id)
        self.session.flush()
        self.session.expire(parking_lot, ['extensions'])

    def dissociate_parking_lot(self, parking_lot, extension):
        if parking_lot is extension.parking_lot:
            extension.type = 'user'
            extension.typeval = '0'
            self.session.flush()
            self.session.expire(parking_lot, ['extensions'])

    def _add_tenant_filter(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Extension.tenant_uuid.in_(self.tenant_uuids))
