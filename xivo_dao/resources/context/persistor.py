# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from sqlalchemy import or_
from sqlalchemy.orm.attributes import get_history

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextmember import ContextMember
from xivo_dao.alchemy.contextnumbers import ContextNumbers

from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.voicemail import Voicemail

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class ContextPersistor(CriteriaBuilderMixin):

    _search_table = Context

    def __init__(self, session, context_search):
        self.session = session
        self.context_search = context_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Context)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        context = self.find_by(criteria)
        if not context:
            raise errors.not_found('Context', **criteria)
        return context

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.context_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, context):
        self.session.add(context)
        self.session.flush()
        return context

    def edit(self, context):
        self._edit_associations(context)
        self.session.add(context)
        self.session.flush()

    def _edit_associations(self, context):
        name_history = get_history(context, 'name')
        if name_history.has_changes():
            old_name = name_history[2][0]

            tables = [ContextMember,
                      ContextNumbers,
                      AgentFeatures,
                      GroupFeatures,
                      LineFeatures,
                      MeetmeFeatures,
                      QueueFeatures,
                      TrunkFeatures,
                      Extension,
                      Incall,
                      Outcall,
                      Queue,
                      SCCPLine,
                      UserCustom,
                      UserSIP,
                      UserIAX,
                      Voicemail,
                      AgentLoginStatus]

            for table in tables:
                (self.session.query(table)
                 .filter(getattr(table, 'context') == old_name)
                 .update({'context': context.name}))

            (self.session.query(ContextInclude)
             .filter(ContextInclude.context == old_name)
             .update({'context': context.name}))

            (self.session.query(ContextInclude)
             .filter(ContextInclude.include == old_name)
             .update({'include': context.name}))

    def delete(self, context):
        self._delete_associations(context)
        self.session.delete(context)
        self.session.flush()

    def _delete_associations(self, context):
        # Should be deleted when Context will have relationship with ContextInclude
        (self.session.query(ContextInclude)
         .filter(or_(ContextInclude.context == context.name,
                     ContextInclude.include == context.name))
         .delete())

        (self.session.query(ContextMember)
         .filter(ContextMember.context == context.name)
         .delete())
