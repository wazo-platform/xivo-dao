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
from xivo_dao.resources.extension.fixes import ExtensionFixes

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
        user_line = (self.session.query(UserLine)
                     .filter(UserLine.line_id == line.id)
                     .filter(UserLine.user_id == None)  # noqa
                     .first())

        if user_line:
            user_line.user_id = user.id
        else:
            main = self.find_by(main_user=True, line_id=line.id)
            user_line = UserLine(user_id=user.id,
                                 line_id=line.id,
                                 main_line=True,
                                 main_user=(False if main else True),
                                 extension_id=(main.extension_id if main else None))

        self.session.add(user_line)
        self.session.flush()
        self.fix_associations(user_line)

        return user_line

    def associate_line_extension(self, line, extension):
        user_lines = (self.session.query(UserLine)
                     .filter(UserLine.line_id == line.id)
                     .filter(UserLine.extension_id == None)  # noqa
                     .all())

        if len(user_lines) == 0:
            user_lines = [UserLine(line_id=line.id,
                                   main_line=True,
                                   main_user=True)]

        for user_line in user_lines:
            user_line.extension_id = extension.id
            self.session.add(user_line)
            self.session.flush()
            self.fix_associations(user_line)

        return user_lines

    def dissociate_user_line(self, user, line):
        user_line = self.get_by(user_id=user.id, line_id=line.id)
        self.delete_queue_member(user_line)

        if user_line.extension_id is None or not user_line.main_user:
            self.session.delete(user_line)
        else:
            user_line.user_id = None
            self.session.add(user_line)

        self.session.flush()
        self.fix_associations(user_line)

        return user_line

    def delete_queue_member(self, user_line):
        (self.session.query(QueueMember)
         .filter(QueueMember.usertype == 'user')
         .filter(QueueMember.userid == user_line.user_id)
         .delete())

    def dissociate_line_extension(self, line, extension):
        user_lines = self.find_all_by(line_id=line.id, extension_id=extension.id)
        for user_line in user_lines:

            if user_line.user_id is None:
                self.session.delete(user_line)
            else:
                user_line.extension_id = None
                self.session.add(user_line)

            self.session.flush()
            self.fix_associations(user_line)

        return user_lines

    def fix_associations(self, user_line):
        if user_line.user_id and user_line.main_user:
            UserFixes(self.session).fix_user(user_line.user_id)
        if user_line.line_id and user_line.main_line:
            LineFixes(self.session).fix(user_line.line_id)
        if user_line.extension_id:
            ExtensionFixes(self.session).fix_extension(user_line.extension_id)
