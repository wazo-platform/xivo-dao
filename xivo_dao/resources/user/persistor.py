# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unicodedata

from sqlalchemy.sql import func

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.helpers.db_manager import Session

from xivo_dao.helpers import errors
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class UserPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = User

    def __init__(self, session, user_view, user_search, tenant_uuids=None):
        self.session = session
        self.user_view = user_view
        self.user_search = user_search
        self.tenant_uuids = tenant_uuids

    def find_by_id_uuid(self, id):
        query = self.session.query(User)
        if isinstance(id, int):
            query = query.filter_by(id=id)
        else:
            id = str(id)
            if id.isdigit():
                query = query.filter_by(id=int(id))
            else:
                query = query.filter_by(uuid=id)
        if self.tenant_uuids is not None:
            query = query.filter(User.tenant_uuid.in_(self.tenant_uuids))
        return query.first()

    def get_by_id_uuid(self, id):
        user = self.find_by_id_uuid(id)
        if not user:
            raise errors.not_found('User', id=id)
        return user

    def find_all_by_agent_id(self, agent_id):
        return self.session.query(User).filter(User.agent.has(id=agent_id)).all()

    def _find_query(self, criteria):
        query = self.session.query(User)
        if self.tenant_uuids is not None:
            query = query.filter(User.tenant_uuid.in_(self.tenant_uuids))
        return self.build_criteria(query, criteria)

    def count_all_by(self, column_name, criteria):
        column = self._get_column(column_name)
        query = self.session.query(column, func.count(column).label('count'))
        query = self.build_criteria(query, criteria)
        query = query.group_by(column)
        return query.all()

    def search(self, parameters, is_db_sort_limit=True):
        view = self.user_view.select(parameters.get('view'))
        query = view.query(self.session)
        if self.tenant_uuids is not None:
            query = query.filter(User.tenant_uuid.in_(self.tenant_uuids))

        if not is_db_sort_limit:
            order = parameters.pop('order', None)
            limit = parameters.pop('limit', None)
            offset = parameters.pop('offset', None)
            reverse = False if parameters.pop('direction', 'asc') == 'asc' else True

        rows, total = self.user_search.search_from_query(query, parameters)
        users = view.convert_list(rows)
        if is_db_sort_limit:
            return SearchResult(total, users)
        else:
            result = sorted(
                users,
                key=lambda x: unicodedata.normalize('NFKD', x.__getattribute__(order)),
                reverse=reverse,
            )

            if not offset or not limit:
                return SearchResult(total, result[offset:])
            else:
                return SearchResult(total, result[offset : offset + limit])

    def create(self, user):
        self.prepare_template(user)
        user.fill_caller_id()

        self.session.add(user)
        self.session.flush()

        return user

    def prepare_template(self, user):
        if not user.func_key_private_template_id:
            template = FuncKeyTemplate(tenant_uuid=user.tenant_uuid, private=True)
            user.func_key_template_private = template

    def associate_all_groups(self, user, groups):
        with Session.no_autoflush:
            user.groups = groups
            for member in user.group_members:
                member.user = user
                member.fix()
        self.session.flush()
