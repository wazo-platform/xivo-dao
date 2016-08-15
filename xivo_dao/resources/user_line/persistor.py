# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_dao.resources.utils.search import CriteriaBuilderMixin
from xivo_dao.resources.user.fixes import UserFixes
from xivo_dao.resources.line.fixes import LineFixes

from xivo_dao.helpers import errors
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.queuemember import QueueMember


class Persistor(CriteriaBuilderMixin):

    _search_table = UserLine

    def __init__(self, session, resource, exclude):
        self.session = session
        self.resource = resource
        self.exclude = exclude

    def find_query(self, criteria):
        column = getattr(UserLine, self.exclude)
        query = self.session.query(UserLine).filter(column != None)  # noqa
        return self.build_criteria(query, criteria)

    def find_by(self, **criteria):
        return self.find_query(criteria).first()

    def get_by(self, **criteria):
        user_line = self.find_by(**criteria)
        if not user_line:
            raise errors.not_found(self.resource, **criteria)
        return user_line

    def find_all_by(self, **criteria):
        return self.find_query(criteria).all()

    def associate_user_line(self, user, line):
        main_user_line = self.find_by(main_user=True, line_id=line.id)
        user_main_line = self.find_by(main_line=True, user_id=user.id)

        user_line = UserLine(user_id=user.id,
                             line_id=line.id,
                             main_line=(False if user_main_line else True),
                             main_user=(False if main_user_line else True))

        self.session.add(user_line)
        self.session.flush()
        self.fix_associations(user_line)

        return user_line

    def dissociate_user_line(self, user, line):
        user_line = self.get_by(user_id=user.id, line_id=line.id)
        self.delete_queue_member(user_line)

        if user_line.main_line:
            self._set_oldest_main_line(user)

        self.session.delete(user_line)
        self.session.flush()
        self.fix_associations(user_line)

        return user_line

    def delete_queue_member(self, user_line):
        (self.session.query(QueueMember)
         .filter(QueueMember.usertype == 'user')
         .filter(QueueMember.userid == user_line.user_id)
         .delete())

    def _set_oldest_main_line(self, user):
        oldest_user_line = (self.session.query(UserLine)
                            .filter(UserLine.user_id == user.id)
                            .filter(UserLine.main_line == False)  # noqa
                            .order_by(UserLine.line_id.asc())
                            .first())
        if oldest_user_line:
            oldest_user_line.main_line = True
            self.session.add(oldest_user_line)

    def fix_associations(self, user_line):
        if user_line.main_user:
            UserFixes(self.session).fix_user(user_line.user_id)
        LineFixes(self.session).fix(user_line.line_id)
