# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.entity import Entity

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult


class UserPersistor(object):

    def __init__(self, session, user_view, user_search):
        self.session = session
        self.user_view = user_view
        self.user_search = user_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(User)
        for name, value in criteria.iteritems():
            column = self._get_column(name)
            query = query.filter(column == value)
        return query

    def _get_column(self, name):
        column = getattr(User, name, None)
        if column is None:
            raise errors.unknown(name)
        return column

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
        (self.session.query(QueueMember).filter(QueueMember.usertype == 'user')
         .filter(QueueMember.userid == user.id)
         .delete())
        (self.session.query(RightCallMember).filter(RightCallMember.type == 'user')
         .filter(RightCallMember.typeval == str(user.id))
         .delete())
        (self.session.query(Callfiltermember).filter(Callfiltermember.type == 'user')
         .filter(Callfiltermember.typeval == str(user.id))
         .delete())
        (self.session.query(Dialaction).filter(Dialaction.category == 'user')
         .filter(Dialaction.categoryval == str(user.id))
         .delete())
        (self.session.query(SchedulePath).filter(SchedulePath.path == 'user')
         .filter(SchedulePath.pathid == user.id)
         .delete())
        self.session.delete(user)
        self.session.flush()
