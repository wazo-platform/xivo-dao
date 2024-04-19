# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql import cast
from sqlalchemy.sql.expression import and_, literal_column
from sqlalchemy.types import String

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.query_options import QueryOptionsMixin
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class IncallPersistor(QueryOptionsMixin, CriteriaBuilderMixin, BasePersistor):
    _search_table = Incall

    def __init__(self, session, incall_search, tenant_uuids=None):
        self.session = session
        self.search_system = incall_search
        self.tenant_uuids = tenant_uuids

    def create(self, incall):
        incall.main = not self._is_main_already_exists(incall.tenant_uuid)
        self.session.add(incall)
        self.session.flush()
        return incall

    def _is_main_already_exists(self, tenant_uuid):
        return (
            self.session.query(Incall)
            .filter(Incall.main.is_(True))
            .filter(Incall.tenant_uuid == tenant_uuid)
            .first()
        )

    def _find_query(self, criteria):
        query = self._generate_query()
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self._generate_query()

    def delete(self, incall):
        self._delete_associations(incall)
        self.session.delete(incall)
        self.session.flush()

    def _delete_associations(self, incall):
        (
            self.session.query(Extension)
            .filter(Extension.type == 'incall')
            .filter(Extension.typeval == str(incall.id))
            .update({'type': 'user', 'typeval': '0'})
        )

    def find_main_callerid(self, tenant_uuid):
        query = (
            self.session.query(
                Extension.exten.label('number'),
                literal_column("'main'").label('type'),
            )
            .select_from(Incall)
            .join(
                Extension,
                and_(
                    Extension.type == 'incall',
                    Extension.typeval == cast(Incall.id, String),
                ),
            )
            .filter(
                Incall.tenant_uuid == tenant_uuid,
                Incall.main.is_(True),
            )
        )
        return query.first()
