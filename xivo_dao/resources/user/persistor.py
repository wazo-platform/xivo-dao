# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql import cast, func
from sqlalchemy.sql.expression import and_, literal_column
from sqlalchemy.types import String

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers import errors
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.query_options import QueryOptionsMixin
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class UserPersistor(QueryOptionsMixin, CriteriaBuilderMixin, BasePersistor):
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

    def _search(self, parameters, is_collated=False):
        view = self.user_view.select(
            parameters.get('view'),
            default_query=self._generate_query(),
        )
        query = view.query(self.session)
        if self.tenant_uuids is not None:
            query = query.filter(User.tenant_uuid.in_(self.tenant_uuids))
        if not is_collated:
            rows, total = self.user_search.search_from_query(query, parameters)
        else:
            rows, total = self.user_search.search_from_query_collated(query, parameters)
        users = view.convert_list(rows)
        return SearchResult(total, users)

    def search(self, parameters):
        return self._search(parameters)

    def search_collated(self, parameters):
        return self._search(parameters, is_collated=True)

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

    def list_outgoing_callerid_associated(self, user_id):
        query = (
            self.session.query(
                Extension.exten.label('number'),
                literal_column("'associated'").label('type'),
            )
            .select_from(Incall)
            .join(
                Dialaction,
                and_(
                    Dialaction.category == 'incall',
                    Dialaction.categoryval == cast(Incall.id, String),
                ),
            )
            .join(
                Extension,
                and_(
                    Extension.type == 'incall',
                    Extension.typeval == cast(Incall.id, String),
                ),
            )
            .filter(
                and_(
                    Dialaction.action == 'user',
                    Dialaction.actionarg1 == str(user_id),
                )
            )
        )
        return query.all()
