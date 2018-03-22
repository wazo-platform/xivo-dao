# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Session

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class UserPersistor(CriteriaBuilderMixin):

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

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(User)
        if self.tenant_uuids is not None:
            query = query.filter(User.tenant_uuid.in_(self.tenant_uuids))
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        user = self.find_by(criteria)
        if not user:
            raise errors.not_found('User', **criteria)
        return user

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        view = self.user_view.select(parameters.get('view'))
        query = view.query(self.session)
        if self.tenant_uuids is not None:
            query = query.filter(User.tenant_uuid.in_(self.tenant_uuids))
        rows, total = self.user_search.search_from_query(query, parameters)
        users = view.convert_list(rows)
        return SearchResult(total, users)

    def create(self, user):
        self.prepare_template(user)
        self.prepare_entity(user)
        user.fill_caller_id()

        self.session.add(user)
        self.session.flush()

        return user

    def prepare_template(self, user):
        if not user.has_private_template():
            template = FuncKeyTemplate(private=True)
            user.func_key_template_private = template

    def prepare_entity(self, user):
        if not user.has_entity():
            user.entity_id = Entity.query_default_id().as_scalar()

    def edit(self, user):
        self.session.add(user)
        self.session.flush()

    def delete(self, user):
        (self.session.query(RightCallMember).filter(RightCallMember.type == 'user')
         .filter(RightCallMember.typeval == str(user.id))
         .delete())
        (self.session.query(Dialaction).filter(Dialaction.category == 'user')
         .filter(Dialaction.categoryval == str(user.id))
         .delete())
        self.session.delete(user)
        self.session.flush()

    def associate_all_groups(self, user, groups):
        with Session.no_autoflush:
            user.groups = groups
            for member in user.group_members:
                member.user = user
                member.fix()
        self.session.flush()
